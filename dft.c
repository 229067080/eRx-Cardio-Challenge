//config
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define DFT -1      //Sign in exponent; determines if
#define IDFT 1      //transform is forward or inverse
#define dN 4479     //length of data
#define T 60.0      //time period
#define MIN 50      //freq range for bandpass filter
#define MAX 300

//complex number struct
typedef struct {
	double re;
	double im; 
} cnum;

//cnum magnitude function
double mag(cnum z) {
	return sqrt(z.re * z.re + z.im * z.im);
}

//multiply two cnums
cnum multiply(cnum w, cnum z) {
	return (cnum){w.re*z.re - w.im*z.im,w.re*z.im + w.im*z.re};
}

//e^{+/- 2*pi*n*k/N}
cnum factor(int n, int k, int N, int sign) {
	return (cnum){cos(2*M_PI*n*k/N),sin(sign*2*M_PI*n*k/N)};
}

//write complex numbers to a file
void writefile(FILE *f,double t, cnum h){
	fprintf(f, "%lf,%lf,%lf\n", t, h.re, h.im);
}



//DFT or IDFT depending on the first parameter
cnum *transform(int sign, cnum *hs, int N) {

	cnum *results = (cnum *)malloc((size_t)N * sizeof(cnum));
	if (results == NULL) {
		printf("\nProblem with memory allocation\n\n");
		exit(EXIT_FAILURE);
	}

	//Iterate for each term in the transform
	for (int n=0;n<N;n++) {
		cnum h = {0,0};
		
		//Iterate for the sum in the transform
		for (int k=0;k<N;k++) {
			cnum c = multiply(hs[k],factor(n,k,N,sign));

			//If IDFT, normalise results.
			if (sign == 1) {
				h.re += c.re/N;
				h.im += c.im/N;
			} else {
				h.re += c.re;
				h.im += c.im;
			}
		}
		results[n] = h;
	}
	return results;
}


int main() {
	
	char filenames[10][50] = {
		"data/2022-06-07 11-04-55.csv",
		"data/2022-06-07 09-15-58.csv",
		"data/2022-06-07 11-22-35.csv",
		"data/2022-06-14 09-42-01.csv",
		"data/2022-06-07 09-51-55.csv",
		"data/2022-06-14 09-31-19.csv",
		"data/2022-06-14 12-55-43.csv",
		"data/2022-06-14 11-07-24.csv",
		"data/2022-06-14 11-55-02.csv",
		"data/2022-06-07 10-03-36.csv",
	};

	for (int q=0;q<10;q++) {
		//Open csv
		FILE *f1 = fopen(filenames[q],"r");
		if (f1 == NULL) {
			printf("Problem opening file");
			return 1;
		}

		//Reading data into an array.
		cnum inputArray[dN];

		int c;
		while ((c = fgetc(f1)) != EOF && c != '\n');

		for (int i = 0; i < dN; i++) {
			fscanf(f1, "%*lf,%*lf,%lf,%*lf,%*lf", &inputArray[i].re);
			inputArray[i].im = 0;
		}

		
		//DFT data.
		cnum *dftArray = transform(DFT, inputArray, dN);

		//filter
		
		for (int i=0;i<MIN;i++) {
			dftArray[i].re = 0;
			dftArray[i].im = 0;
		}

		for (int i=MAX;i<dN;i++) {
			dftArray[i].re = 0;
			dftArray[i].im = 0;
		}
		
		//Find largest freq contributor

		double largest = 0;
		int index = 0;
		double current;

		for (int i=MIN;i<MAX;i++) {
			current = mag(dftArray[i]);
			if (current>largest) {
				index = i;
				largest = current;
			}
		}

		cnum *outputArray = transform(IDFT, dftArray, dN);

		char o_filename[50];
		strcpy(o_filename, filenames[q]);
		strcat(o_filename, " output.csv");

		printf("\nLargest f contributor = %d\n",index);

		FILE *f2 = fopen(o_filename,"w");
		if (f2 == NULL) {
			printf("Problem with opening output.csv");
			return 1;
		}

		//Writing IDFT-ed data to file.
		for (int i=0;i<dN;i++) {
			double t = i * T/dN;
			writefile(f2, t, outputArray[i]);
		}
		
		//tying up loose ends
		free(dftArray);
		free(outputArray);
	}
	return 0;
}
