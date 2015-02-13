#include "fglove.h"

using namespace std;

fdGlove *pGlove;

bool setup(){
    char port[] = "/dev/usb/hiddev0";
	pGlove = fdOpen(port); // connects to the first glove it finds
	if (pGlove){ 
		return true;
	}else{
		return false;
	}
	
	//fdSetAutoCalibrate(pGlove,true);
}

float poll_raw(int n){
	return fdGetSensorRaw(pGlove,n);
}

float poll(int n){
    return fdGetSensorScaled(pGlove,n);
}

int getGesture(){
	return fdGetGesture(pGlove);
} 

int getAutoCalibration_lower(int n){
        short unsigned int lower;
        short unsigned int upper;
	fdGetCalibration(pGlove, n, &lower, &upper);
        return lower;
}

int getAutoCalibration_upper(int n){
        short unsigned int lower;
        short unsigned int upper;
	fdGetCalibration(pGlove, n, &lower, &upper);
        return upper;
}

bool close(){
	fdClose(pGlove);
	return true;
}
