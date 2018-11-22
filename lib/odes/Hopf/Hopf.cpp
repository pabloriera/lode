#define PI 3.141592653589793238462

#define N_EQ 2
#define N_PARAMETERS 2

extern "C"
{


	void dimensions(int x[])
	{
		x[0] = N_EQ;
		x[1] = N_PARAMETERS;
	}

	void equation(float X[], float dX[], float param[])
	{
	dX[0]=-2*PI*X[1]*param[1] + (param[0]*X[0]-X[0]*(X[1]*X[1]+X[0]*X[0]))*100.0;
    dX[1]=2*PI*X[0]*param[1] + (param[0]*X[1]-X[1]*(X[1]*X[1]+X[0]*X[0]))*100.0;
	}

}