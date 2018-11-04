#define PI 3.141592653589793238462

#define N_EQ 3
#define N_PARAMETERS 4

extern "C"
{


	void dimensions(int x[])
	{
		x[0] = N_EQ;
		x[1] = N_PARAMETERS;
	}

	void equation(float X[], float dX[], float param[])
	{
	dX[0]=param[2]*(X[2]-X[0])*param[3];
    dX[1]=(X[0]*X[2]-param[0]*X[1])*param[3];
    dX[2]=(X[0]*(param[1]-X[1])-X[2])*param[3];
	}

}