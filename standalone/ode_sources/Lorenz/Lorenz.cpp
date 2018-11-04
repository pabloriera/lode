#include "SC_PlugIn.h"
// #include <dlfcn.h>
    

// InterfaceTable contains pointers to functions in the host (server).
static InterfaceTable *ft;

#define PI 3.141592653589793238462


void equations( float *X,float *dX, float *param)
{

    dX[0]=param[2]*(X[1]-X[0])*param[3];
    dX[1]=(X[0]*(param[1]-X[2])-X[1])*param[3];
    dX[2]=(X[0]*X[1]-param[0]*X[2])*param[3];
}
    
// declare struct to hold unit generator state
struct Lorenz : public Unit
{
    float dt;
    float *X;
    float *param;
    float *F1, *F2, *F3, *F4, *xtemp;
    // float *setX;
    // float *x_prev;
    // float *t;

    int N_EQ, N_PARAMETERS;

};

void rk4(Lorenz* unit)
{

    // Runge-Kutta integrator (4th order)
    // Inputs
    //   X          Current value of dependent variable
    //   n_eq         Number of elements in dependent variable X
    //   t          Independent variable (usually time)
    //   dt        Step size (usually time step)
    //   derivsRK   Right hand side of the Lorenz; derivsRK is the
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
    equations( X, F1, param);
    

    //* Evaluate F2 = f( X+dt*F1/2, t+dt/2 ).
    float half_dt = 0.5*dt;
    //float t_half = t + half_dt;
    int i;

    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F1[i];

    equations( Xtemp, F2, param);

    //* Evaluate F3 = f( X+dt*F2/2, t+dt/2 ).
    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + half_dt*F2[i];

    equations( Xtemp, F3, param);

    //* Evaluate F4 = f( X+dt*F3, t+dt ).
    //float t_full = t + dt;

    for( i=0; i<n_eq; i++ )
        Xtemp[i] = X[i] + dt*F3[i];

    equations( Xtemp, F4, param);

    //* Return X(t+dt) computed from fourth-order R-K.
    for( i=0; i<n_eq; i++ )
        X[i] += dt/6.*(F1[i] + F4[i] + 2.*(F2[i]+F3[i]));


}



// declare unit generator functions
static void Lorenz_next_a(Lorenz *unit, int inNumSamples);
static void Lorenz_next_k(Lorenz *unit, int inNumSamples);
static void Lorenz_Ctor(Lorenz* unit);
static void Lorenz_Dtor(Lorenz* unit);


//////////////////////////////////////////////////////////////////

// Ctor is called to initialize the unit generator.
// It only executes once.

// A Ctor usually does 3 things.
// 1. set the calculation function.
// 2. initialize the unit generator state variables.
// 3. calculate one sample of output.
void Lorenz_Ctor(Lorenz* unit)
{
    printf("Lorenz v0.2\n");
    printf("SAMPLEDUR %g\n",SAMPLEDUR);
    printf("mBufLength %d\n",unit->mBufLength );
    // printf("calc_FullRate %d\n",calc_FullRate);

    // 1. set the calculation function.
    int modRate = calc_BufRate;


    SETCALC(Lorenz_next_a);
  
    // filename = 
    // printf("Library file %s\n",filename);

    //dynamic shared lib
    // void* handle = dlopen("./hopf.so", RTLD_LAZY);


    // if(handle!=NULL)
    // {
      // unit->equation = ( equation_def ) dlsym(handle, "equation");
      // void (*dimensions)(int*) ;
      // dimensions = ( void (*)(int*) ) dlsym(handle, "dimensions");
      // dimensions(dims);
      
      // unit->N_EQ = dims[0];
      // unit->N_PARAMETERS = dims[1];

      // unit->equation = 

    unit->N_EQ = 3;
    unit->N_PARAMETERS = 4;

    // unit->setX =  (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
    // unit->x_prev =  (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );

    unit->F1 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
    unit->F2 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
    unit->F3 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
    unit->F4 = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );
    unit->xtemp = (float *)RTAlloc(unit->mWorld, unit->N_EQ * sizeof(float) );

    unit->X = (float*) RTAlloc(unit->mWorld,unit->N_EQ*sizeof(float));
    unit->param = (float*) RTAlloc(unit->mWorld,unit->N_PARAMETERS*sizeof(float));

    unit->dt = SAMPLEDUR;
 
    // }

    for(int k=0;k<unit->N_EQ;k++)
        unit->X[k] = 0.001;

    for(int k=0;k<unit->N_PARAMETERS;k++)
    {
        unit->param[k] = IN0(k);
        printf("PARAM %g\n",unit->param[k]);
    }

    for(int k=0;k<unit->N_EQ;k++)
    {
        OUT0(k) = unit->X[k];
    }

    rk4(unit);

    printf("OUT %g\n",unit->X[0]);

    // printf("OUT %g\n",ZOUT(0)[0]);

    // Lorenz_next_k(unit, 1);
}

void Lorenz_Dtor(Lorenz* unit)
{
    RTFree(unit->mWorld, unit->X );
    RTFree(unit->mWorld, unit->param );
    RTFree(unit->mWorld, unit->F1 );
    RTFree(unit->mWorld, unit->F2 );
    RTFree(unit->mWorld, unit->F3 );
    RTFree(unit->mWorld, unit->F4 );
    RTFree(unit->mWorld, unit->xtemp );
}

//////////////////////////////////////////////////////////////////

// The calculation function executes once per control period
// which is typically 64 samples.

// calculation function for an audio rate frequency argument
void Lorenz_next_a(Lorenz *unit, int inNumSamples)
{

    for (int i=0; i < inNumSamples; ++i)
    {
        for(int k=0;k<unit->N_PARAMETERS;k++)
        {
            unit->param[k] = IN(k)[i];
        }

        rk4( unit  );

        for(int k=0;k<unit->N_EQ;k++)
        {
            OUT(k)[i] = unit->X[k];
        }
    }
}

//////////////////////////////////////////////////////////////////

void Lorenz_next_k(Lorenz *unit, int inNumSamples)
{

    for (int i=0; i < inNumSamples; ++i)
    {

        for(int k=0;k<unit->N_PARAMETERS;k++)
        {
            unit->param[k] = IN0(k);
        }

        rk4( unit );

        for(int k=0;k<unit->N_EQ;k++)
        {
            OUT(k)[i] = unit->X[k];
        }
    }

}

// the entry point is called by the host when the plug-in is loaded
PluginLoad(Lorenz)
{
    // InterfaceTable *inTable implicitly given as argument to the load function
    ft = inTable; // store pointer to InterfaceTable

    DefineSimpleUnit(Lorenz);
}
