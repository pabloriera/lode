#include <math.h>
#include <iostream>
#define PI 3.141592653589793238462
#define N_EQ $N_EQ
#define N_PARAMETERS $N_PARAMETERS

extern "C"
{

    $FUNCTIONS

    void dimensions(int x[])
    {
        x[0] = N_EQ;
        x[1] = N_PARAMETERS;
    }

    void equation(double X[], $TorN, double dX[], double param[])
    {
    $EQUATION
    }

}