#define PI 3.141592653589793238462

#include "m_pd.h"

#define N_EQ $N_EQ
#define N_PARAMETERS $N_PARAMETERS

void dimensions(int x[])
{
	x[0] = N_EQ;
	x[1] = N_PARAMETERS;
}

void equation(t_sample X[], t_sample t, t_sample param[], t_sample dX[] )
{
$EQUATION
}
