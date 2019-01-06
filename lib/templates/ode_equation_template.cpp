#include <math.h>
#include <iostream>
#define PI 3.141592653589793238462
#define N_EQ $N_EQ
#define N_PARAMETERS $N_PARAMETERS
// #define PRINT

extern "C"
{

    $FUNCTIONS

    void dimensions(int x[])
    {
        x[0] = N_EQ;
        x[1] = N_PARAMETERS;
    }

    void equation(double X[], double t, double dX[], double param[])
    {
    $EQUATION


    #ifdef PRINT
        std::cout << "t " << t << std::endl;

        std::cout << "X ";
        for(int k=0;k<N_EQ;k++)
        {
            std::cout << X[k] << " ";
        }

        std::cout << "\ndX ";
        for(int k=0;k<N_EQ;k++)
        {
            std::cout << dX[k] << " ";
        }

        std::cout << "\nPARAM ";
        for(int k=0;k<N_PARAMETERS;k++)
        {
            std::cout << param[k] << " ";
        }
        std::cout << std::endl;
    #endif
    }

}