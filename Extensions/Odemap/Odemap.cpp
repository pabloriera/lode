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
          Print("Failed to allocate memory for Odemap ugen.");    \
      }                                                             \
      return;                                                       \
    }

typedef  void (*equation_def)(double X[], int n, double dX[], double param[]);

// InterfaceTable contains pointers to functions in the host (server).
static InterfaceTable *ft;

// declare struct to hold unit generator state
struct Odemap : public Unit
{
    char *m_string;
    int m_string_size;
    int N_EQ, N_PARAMETERS;
    bool ok = false;
    equation_def equation;
    void* handle;
    float counter;
    double n;
    double *X;
    double *X_init;
    double *param;
    double *Xtemp;
    double *dx;
    double freq;
};

void apply_map(Odemap* unit)
{
  

}

// declare unit generator functions
static void Odemap_next_a(Odemap *unit, int inNumSamples);
// static void Odemap_next_k(Odemap *unit, int inNumSamples);
static void Odemap_Ctor(Odemap* unit);
static void Odemap_Dtor(Odemap* unit);

//////////////////////////////////////////////////////////////////

// Ctor is called to initialize the unit generator.
// It only executes once.

// A Ctor usually does 3 things.
// 1. set the calculation function.
// 2. initialize the unit generator state variables.
// 3. calculate one sample of output.
void Odemap_Ctor(Odemap* unit)
{
    printf("Odemap v0.2");
    // printf("SAMPLEDUR %g",SAMPLEDUR);
    // printf("mBufLength %d",unit->mBufLength );
    // printf("calc_FullRate %d",calc_FullRate);

    // set the calculation function.
    SETCALC(Odemap_next_a);

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
    Print("Ode name: %s\n", ode_name.c_str());
    Print("Lib name: %s\n", libname.c_str());
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

      RTALLOC_AND_CHECK(unit->Xtemp, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->X, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->dx, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->X_init, unit->N_EQ * sizeof(double));
      RTALLOC_AND_CHECK(unit->param, unit->N_PARAMETERS * sizeof(double));

      unit->n = 0;

      for(int k=0;k<unit->N_EQ;k++)
      {
          unit->X_init[k] = IN0(unit->m_string_size+1+k);
          unit->X[k] = unit->X_init[k];
      }
        
      unit->freq = IN0(unit->m_string_size+1+unit->N_EQ);
      Print("%s: FREC %g\n", unit->m_string, unit->freq);


      for(int k=0;k<unit->N_PARAMETERS;k++)
      {
          unit->param[k] = IN0(unit->m_string_size+1+k+unit->N_EQ+1);
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

void Odemap_Dtor(Odemap* unit)
{
  if(unit->ok)
  {
    RTFree(unit->mWorld, unit->X );
    RTFree(unit->mWorld, unit->param );
    RTFree(unit->mWorld, unit->Xtemp );
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
void Odemap_next_a(Odemap *unit, int inNumSamples)
{


  int n_eq = unit->N_EQ;
  float counter = unit->counter;
  
  unit->freq = IN0(unit->m_string_size+1+unit->N_EQ);

  float samplesPerCycle;
  // double slope;
  if(unit->freq < unit->mRate->mSampleRate){
    samplesPerCycle = unit->mRate->mSampleRate / sc_max(unit->freq, 0.001f);
    // slope = 1.f / samplesPerCycle;
  }
  else {
    samplesPerCycle = unit->mRate->mSampleRate;
    // slope = 1.f;
  }

    // Print("%s: FREC %g\n", unit->m_string, samplesPerCycle);

  for(int k=0;k<unit->N_EQ;k++)
  {
    double X_init_k = IN0(unit->m_string_size+1+k);
    if(unit->X_init[k]!=X_init_k){
      unit->X_init[k] = X_init_k;
      unit->X[k] = X_init_k;
    }

  }

  for (int i=0; i < inNumSamples; ++i)
  {
    if(counter >= samplesPerCycle){
      counter = 0;


      for(int k=0;k<unit->N_PARAMETERS;k++)
      {
        unit->param[k] = zapgremlins(IN(unit->m_string_size+1+k+unit->N_EQ+1)[i]);
      }

      unit->equation( unit->X, unit->n, unit->Xtemp, unit->param);
      unit->n++;

      for(int k=0;k<unit->N_EQ;k++)
      {
        unit->X[k] = unit->Xtemp[k];
      }


      // Linear Interp
      // for(int k=0;k<unit->N_EQ;k++)
      // {
      //   unit->dx[k] = unit->Xtemp[k] - unit->X[k];
      // }

    }
    counter++;
    

    // Linear Interp
    // unit->X[k]+unit->dx[k]*frac

    for(int k=0;k<unit->N_EQ;k++)
    {
      OUT(k)[i] = zapgremlins(unit->X[k]);
    }

      unit->counter = counter;
  }

}

//////////////////////////////////////////////////////////////////

// void Odemap_next_k(Odemap *unit, int inNumSamples)
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
PluginLoad(Odemap)
{
    // InterfaceTable *inTable implicitly given as argument to the load function
    ft = inTable; // store pointer to InterfaceTable

    DefineDtorUnit(Odemap);
}

