#include "SC_PlugIn.h"
#include <dlfcn.h>
#include <string>  
#include <iostream>

// InterfaceTable contains pointers to functions in the host (server).
static InterfaceTable *ft;

#define PI 3.141592653589793238462
#define MAX_CHANNELS 8

typedef  void (*equation_def)(float X[], float param[],float dX[]);

    
// declare struct to hold unit generator state
struct Oderk4 : public Unit
{
    char *m_string;   
    int m_string_size;

    float dt;
    float *X;
    float *param;
    float *F1, *F2, *F3, *F4, *xtemp;
    equation_def equation;

    int N_EQ, N_PARAMETERS;
    bool ok = false;
};

void rk4(Oderk4* unit)
{

    // Runge-Kutta integrator (4th order)
    // Inputs
    //   X          Current value of dependent variable
    //   n_eq         Number of elements in dependent variable X
    //   t          Independent variable (usually time)
    //   dt        Step size (usually time step)
    //   derivsRK   Right hand side of the Oderk4; derivsRK is the
    //              name of the function which returns dX/dt
    //              Calling format derivsRK(X,t,param,dXdt).
    //   param      Extra parameters passed to derivsRK
    // Output
    //   X          New value of X after a step of size dt

    float dt = unit->dt;
    float *F1, *F2, *F3, *F4, *Xtemp, *X, *param;
    F1 = unit->F1;
    F2 = unit->F2;
    F3 = unit->F3;
    F4 = unit->F4;
    Xtemp = unit->xtemp;
    X = unit->X;
    param = unit->param;

    int n_eq = unit->N_EQ;

    //* Evaluate F1 = f(X,t).
    unit->equation( X, F1, param);
    //* Evaluate F2 = f( X+dt*F1/2, t+dt/2 ).
    float half_dt = 0.5*dt;
    //float t_half = t + half_dt;
    int i;

    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F1[i];

    unit->equation( Xtemp, F2, param);

    //* Evaluate F3 = f( X+dt*F2/2, t+dt/2 ).
    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F2[i];

    unit->equation( Xtemp, F3, param);

    //* Evaluate F4 = f( X+dt*F3, t+dt ).
    //float t_full = t + dt;

    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + dt*F3[i];

    unit->equation( Xtemp, F4, param);

    //* Return X(t+dt) computed from fourth-order R-K.
    for( i=0; i<n_eq; i++ )
        X[i] += dt/6.*(F1[i] + F4[i] + 2.*(F2[i]+F3[i]));

}


// declare unit generator functions
static void Oderk4_next_a(Oderk4 *unit, int inNumSamples);
// static void Oderk4_next_k(Oderk4 *unit, int inNumSamples);
static void Oderk4_Ctor(Oderk4* unit);
static void Oderk4_Dtor(Oderk4* unit);

//////////////////////////////////////////////////////////////////

// Ctor is called to initialize the unit generator.
// It only executes once.

// A Ctor usually does 3 things.
// 1. set the calculation function.
// 2. initialize the unit generator state variables.
// 3. calculate one sample of output.
void Oderk4_Ctor(Oderk4* unit)
{
    printf("Oderk4 v0.2\n");
    // printf("SAMPLEDUR %g\n",SAMPLEDUR);
    // printf("mBufLength %d\n",unit->mBufLength );
    // printf("calc_FullRate %d\n",calc_FullRate);

    // 1. set the calculation function.
    int modRate = calc_BufRate;
    SETCALC(Oderk4_next_a);

    unit->m_string_size = IN0(0); // number of chars in the id string
    // unit->m_string = (char*)RTAlloc(unit->mWorld, unit->m_string_size * sizeof(char));
    unit->m_string = (char*)malloc(unit->m_string_size * sizeof(char)); 
    // Print("m_string %s\n",unit->m_string);
    // Print("string length %d\n", unit->m_string_size);
    for(int i = 0; i < unit->m_string_size; i++){
        // char aux[1];
        // aux[0]= (char)IN0(1+i);
        // printf("letter %d: %s\n", i, aux);
        unit->m_string[i] = (char)IN0(1+i);
    };
    std::string ode_name(unit->m_string);
    // Print("Ode name %s\n",unit->m_string);
    // Print("Ode name %s\n",ode_name.c_str());
    std::string libname("odes/lib"+ode_name+".so");
    std::cout << "Ode name: " << ode_name << std::endl;
    std::cout << "Lib name: " << libname  << std::endl;
    void* handle = dlopen(libname.c_str(), RTLD_LAZY);
    
    if(handle!=NULL)
    {
      Print("dl opened\n");
      void (*dimensions)(int*);
      dimensions = ( void (*)(int*) ) dlsym(handle, "dimensions");
      int dims[2];
      dimensions(dims);
      printf("dimensions %d\t%d\n", dims[0],dims[1]);

      unit->equation = ( equation_def ) dlsym(handle, "equation");      

      unit->N_EQ = dims[0];
      unit->N_PARAMETERS = dims[1];

      Print("N_PARAMETERS %d\n",unit->N_PARAMETERS);
      Print("N_EQ %d\n",unit->N_EQ);

      unit->F1 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
      unit->F2 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
      unit->F3 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
      unit->F4 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
      unit->xtemp = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );

      unit->X = (float*) RTAlloc(unit->mWorld,unit->N_EQ*sizeof(float));
      unit->param = (float*) RTAlloc(unit->mWorld,unit->N_PARAMETERS*sizeof(float));

      unit->dt = SAMPLEDUR;

      for(int k=0;k<unit->N_EQ;k++)
          unit->X[k] = 0.001;

      for(int k=0;k<unit->N_PARAMETERS;k++)
      {
          unit->param[k] = IN0(unit->m_string_size+1+k);
          Print("PARAM %g\n", unit->param[k]);
      }

      for(int k=0;k<unit->N_EQ;k++)
      {
          OUT0(k) = unit->X[k];
      }

      unit->ok = true;
    }
    else
    {
      Print("lib.so not open\n");
      for(int k=0;k<MAX_CHANNELS;k++)
      {
          OUT0(k) = 0.0;
      }
    }

}

void Oderk4_Dtor(Oderk4* unit)
{
  if(unit->ok)
  {
    free(unit->m_string);
    RTFree(unit->mWorld, unit->X );
    RTFree(unit->mWorld, unit->param );
    RTFree(unit->mWorld, unit->F1 );
    RTFree(unit->mWorld, unit->F2 );
    RTFree(unit->mWorld, unit->F3 );
    RTFree(unit->mWorld, unit->F4 );
    RTFree(unit->mWorld, unit->xtemp );
  }
}

//////////////////////////////////////////////////////////////////

// The calculation function executes once per control period
// which is typically 64 samples.

// calculation function for an audio rate frequency argument
void Oderk4_next_a(Oderk4 *unit, int inNumSamples)
{

    for (int i=0; i < inNumSamples; ++i)
    {
        for(int k=0;k<unit->N_PARAMETERS;k++)
        {
            unit->param[k] = IN(unit->m_string_size+1+k)[i];
        }

        rk4( unit );

        for(int k=0;k<unit->N_EQ;k++)
        {
            OUT(k)[i] = zapgremlins(unit->X[k]);
        }
    }
}

//////////////////////////////////////////////////////////////////

// void Oderk4_next_k(Oderk4 *unit, int inNumSamples)
// {

//     for (int i=0; i < inNumSamples; ++i)
//     {

//         for(int k=0;k<unit->N_PARAMETERS;k++)
//         {
//             unit->param[k] = IN0(k);
//         }

//         rk4( unit );

//         for(int k=0;k<unit->N_EQ;k++)
//         {
//             OUT(k)[i] = unit->X[k];
//         }
//     }

// }

// the entry point is called by the host when the plug-in is loaded
PluginLoad(Oderk4)
{
    // InterfaceTable *inTable implicitly given as argument to the load function
    ft = inTable; // store pointer to InterfaceTable

    DefineSimpleUnit(Oderk4);
}
