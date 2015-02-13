#include <Python.h>
#include <iostream>
#include <iomanip>
#include <string>
#include "fglove.h"

using namespace std;

fdGlove *pGlove = NULL;


bool setup(){
	//a = fdOpen("DG5U_L"); //or you may use DG14U_R, DG14U_L, DG5U_R
	//a = fdOpen("DG14U_L");
	pGlove = fdOpen(""); // connects to the first glove it finds
	if pGlove return true;
	else return false;
}

float* poll(){
	float values[14]
	for (int n=0; n<14;n++)
	{
		a[n] = fdGetSensorScaled(pGlove, n);
	}
	return n;
}

bool close(){
	fdClose(pGlove);
	return true;
}

int main (int argc, char * const argv[]) 
{

	std::cout << "num USB found" << fdScanUSB() << "\n";


	if (pGlove) 
	{
		cout<<"found glove \n";
		cout<<"type: "<<fdGetGloveType(pGlove)<<" handedness: "<<fdGetGloveHand(pGlove)<<"\n";
		cout<<"packet rate: "<<fdGetPacketRate(pGlove)<<"\n";
		cout<<"version number major: "<<fdGetFWVersionMajor(pGlove)<<"."<<fdGetFWVersionMinor(pGlove);
		
		for (int i=0; i<100000; i++)
		{
			
			cout <<"\n";
		}
		
	}
	
	fdClose(pGlove);

    cout << "finished.\n";
    return 0;
}
