#include "SC_PlugIn.h"
#include <dlfcn.h>
#include <string>  
#include <iostream>
#define PI 3.141592653589793238462
#define MAX_CHANNELS 8

#define typeof(x) __typeof__(x)

#define RTALLOC_AND_CHECK(lhs, size)                                \
    (lhs) = (typeof(lhs)) RTAlloc(unit->mWorld, (size));            \
    memset((lhs), 0, (size));                                       \
    if (!(lhs)) {                                                   \
      SETCALC(ClearUnitOutputs);                                    \
      ClearUnitOutputs(unit, 1);                                    \
      if (unit->mWorld->mVerbosity > -2) {                          \
          Print("Failed to allocate memory for Oderk4 ugen.");    \
      }                                                             \
      return;                                                       \
    }

typedef  void (*equation_def)(double X[], double t, double dX[], double param[]);

// InterfaceTable contains pointers to functions in the host (server).
static InterfaceTable *ft;

// declare struct to hold unit generator state
struct Oderk4 : public Unit
{
    char *m_string;
    int m_string_size;
    int N_EQ, N_PARAMETERS;
    int c=0;
    bool ok = false;
    equation_def equation;
    void* handle;
    double dt;
    double t;
    double *X;
    double *X_init;
    double *param;
    double *F1, *F2, *F3, *F4, *xtemp;    
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
    int n_eq = unit->N_EQ;
    int i;
    double dt = unit->dt;
    double t = unit->t;
    double half_dt = 0.5*dt;
    double t_half = t + half_dt;
    double t_full = t + dt;
    double *F1, *F2, *F3, *F4, *Xtemp, *X, *param;
    F1 = unit->F1;
    F2 = unit->F2;
    F3 = unit->F3;
    F4 = unit->F4;
    Xtemp = unit->xtemp;
    X = unit->X;
    param = unit->param;
    
    // Evaluate F1 = f(X,t).
    unit->equation( X, t, F1, param);
    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F1[i];
    // Evaluate F2 = f( X+dt*F1/2, t+dt/2 ).      
    unit->equation( Xtemp, t_half, F2, param);   
    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F2[i];
    // Evaluate F3 = f( X+dt*F2/2, t+dt/2 ).
    unit->equation( Xtemp, t_half, F3, param );
    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + dt*F3[i];
    // Evaluate F4 = f( X+dt*F3, t+dt ).
    unit->equation( Xtemp, t_full, F4, param);
    // Return X(t+dt) computed from fourth-order R-K.
    for( i=0; i<n_eq; i++ )
      X[i] += dt/6.*(F1[i] + F4[i] + 2.*(F2[i]+F3[i]));
    unit->t = t_full;
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
    printf("Oderk4 v0.2");
    // printf("SAMPLEDUR %g",SAMPLEDUR);
    // printf("mBufLength %d",unit->mBufLength );
    // printf("calc_FullRate %d",calc_FullRate);

    // set the calculation function.
    SETCALC(Oderk4_next_a);

    unit->c = 0;
    unit->m_string_size = IN0(0); // number of chars in the id string
    unit->m_string = (char*) RTAlloc(unit->mWorld, (unit->m_string_size + 1) * sizeof(char));
    for(int i = 0; i < unit->m_string_size; i++){
        unit->m_string[i] = (char)IN0(1+i);
    };
    unit->m_string[unit->m_string_size] = 0;  // terminate string
    std::string ode_name(unit->m_string);
    // Print("Ode name %s",unit->m_string);
    // Print("Ode name %s",ode_name.c_str());
    std::string libname("odes/lib"+ode_name+".so");
    Print("Ode name: %s", ode_name.c_str());
    Print("Lib name: %s", libname.c_str());
    unit->handle = dlopen(libname.c_str(), RTLD_LAZY);

    if(unit->handle!=NULL)
    {
      Print("%s: DLOPEN: ok\n", unit->m_string);
      void (*dimensions)(int*);
      dimensions = ( void (*)(int*) ) dlsym(unit->handle, "dimensions");
      int dims[2];
      dimensions(dims);
      unit->equation = ( equation_def ) dlsym(unit->handle, "equation");      

      unit->N_EQ = dims[0];
      unit->N_PARAMETERS = dims[1];

      Print("%s: N_PARAMETERS %d\n", unit->m_string,unit->N_PARAMETERS);
      Print("%s: N_EQ %d\n", unit->m_string,unit->N_EQ);

      RTALLOC_AND_CHECK(unit->F1, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->F2, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->F3, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->F4, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->xtemp, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->X, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->X_init, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->param, unit->N_PARAMETERS * sizeof(double));

      unit->dt = SAMPLEDUR;
      unit->t = 0;

      for(int k=0;k<unit->N_EQ;k++)
          unit->X[k] = IN0(unit->m_string_size+1+k);

      for(int k=0;k<unit->N_PARAMETERS;k++)
      {
          unit->param[k] = IN0(unit->m_string_size+1+k+unit->N_EQ);
          Print("%s: PARAM %g\n", unit->m_string, unit->param[k]);
      }

      for(int k=0;k<unit->N_EQ;k++)
      {
          OUT0(k) = unit->X[k];
          Print("%s: OUT %g\n", unit->m_string, unit->X[k]);
      }
      unit->ok = true;
    }
    else
    {
      unit->ok = false; 
      SETCALC(ClearUnitOutputs);
      ClearUnitOutputs(unit, 1);
      Print("%s: DLOPEN: not ok\n", unit->m_string);
    }
}

void Oderk4_Dtor(Oderk4* unit)
{
  if(unit->ok)
  {
    RTFree(unit->mWorld, unit->X );
    RTFree(unit->mWorld, unit->X_init );
    RTFree(unit->mWorld, unit->param );
    RTFree(unit->mWorld, unit->F1 );
    RTFree(unit->mWorld, unit->F2 );
    RTFree(unit->mWorld, unit->F3 );
    RTFree(unit->mWorld, unit->F4 );
    RTFree(unit->mWorld, unit->xtemp );
    Print("%s: All Free", unit->m_string);
    dlclose(unit->handle);
    Print("%s: Closed", unit->m_string);
    RTFree(unit->mWorld, unit->m_string);
  }
}

//////////////////////////////////////////////////////////////////

// The calculation function executes once per control period
// which is typically 64 samples.

// calculation function for an audio rate frequency argument
void Oderk4_next_a(Oderk4 *unit, int inNumSamples)
{

    for(int k=0;k<unit->N_EQ;k++)
    {
      if(unit->X_init[k]!=IN0(unit->m_string_size+1+k))
      {
        unit->X_init[k]=IN0(unit->m_string_size+1+k);
        unit->X[k] = unit->X_init[k];
        Print("%s: INIT %g\n", unit->m_string, unit->X_init[k]);
      }
    }

    for (int i=0; i < inNumSamples; ++i)
    {
        for(int k=0;k<unit->N_PARAMETERS;k++)
        {
          unit->param[k] = zapgremlins(IN(unit->m_string_size+1+k+unit->N_EQ)[i]);          
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

    DefineDtorUnit(Oderk4);
}

