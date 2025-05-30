package emart;

import java.util.ArrayList;
import java.util.concurrent.ThreadLocalRandom;

import dataStructure.ActiveSetWR;
import dataStructure.TestFrame;

public class AWSSelectorWR {
	//	numero di failing point
	private int numfp;

	//	stime passo passo
	private double[] z;

	//richieste fallite
	private ArrayList<String> failedRequest;
	
	public AWSSelectorWR() {
		super();
		numfp = 0;
		failedRequest = new ArrayList<String>();
	}

	public double[] getZ() {
		return z;
	}
	
	public int getnumfp(){
		return numfp;
	}
	
	public ArrayList<String> getfailedRequest(){
		return failedRequest;
	}

	/**********************Static Version************************/	
	/* Per poter eseguire l'algoritmo ho bisogno di diverse strutture dati, che in questo caso ci aspettiamo vengano fornite dall'esterno.
Dato che i Test Case vengono selezionati in maniera randomica, si suppone che essi vengano selezionati prima di eseguire l'algoritmo e vengano assegnati alla struttura dati 
dei Test Frame, tenendo conto dell'esito.
I parametri di input considerati sono:
	1) n, numero di campioni da selezionare;
	2) TestFrame, caratterizzato dall'ID (intero compreso tra [0, N-1]), esitoTestCase;
	3) weightsMatrix, matrice dei pesi;
	4) d, che rappresenta la probabilità con cui verrà preferito il campionamento basato su pesi rispetto a quello random.
	 */	
	public double[] selectAndRunTestCase(int n, ArrayList<TestFrame> testFrame, double[][] weightsMatrix, double d){
		/****wr****/
		ArrayList<Integer> sck = new ArrayList<Integer>();
		/****wr****/
		
		failedRequest.clear();
		numfp = 0;

		//Verifica dei dati in input
		if(n <= 0){
			double[] error =  {-1.0, -1.0};
			return error;
		}

		/**************Inizializzazione****************/
		//Definizione delle strutture dati: scompl, valori non ancora selezionati; occurrenceProb, vettore delle probabilità di occorrenza
		double[] occurrenceProb = new double[testFrame.size()];

		for(int i = 0; i < testFrame.size(); i++){
			occurrenceProb[i] = testFrame.get(i).getOccurrenceProb();
			//			System.out.println(occurrenceProb[i]);
		}

//		System.out.println("[DEBUG] Passo 0");

		//Selezione della prima osservazione mediante SRS
		int randomNum = ThreadLocalRandom.current().nextInt(0, testFrame.size());
		/****wr****/
		sck.add(randomNum);
		/****wr****/
		//		System.out.println("[DEBUG] Numero random estratto "+randomNum);

		//		Inizializzazione dell'ActiveSet
		ActiveSetWR ak = new ActiveSetWR(n, testFrame.size(), occurrenceProb);

		String name = testFrame.get(randomNum).getTfID();
		boolean esito = testFrame.get(randomNum).extractAndExecuteTestCase();
		String tc = testFrame.get(randomNum).getReqType()+"\n "+testFrame.get(randomNum).getUrl()+"\n "+testFrame.get(randomNum).getSelPayload();
		//		System.out.println("[DEBUG] il Test Frame selezionato è "+name+ " con esito " +esito);

		//aggiornamento dell'active set e dell'insime dei TF non ancora selezionati
		ak.qiCalculation(d, randomNum);
		ak.activeSetUpdate(name , randomNum, esito, weightsMatrix);

		double y = 0;
		//si suppone esito positivo (true) se viene rilevato un fallimento.
		if (esito) {
			y = 1;
			numfp++;
			this.failedRequest.add(tc);
		}

		//Definizione dell'array contenente le stime passo passo:
		double[] estimationX = new double[n];

		//calcolo del primo valore necessario per la stima (t).
		estimationX[0] = (testFrame.size())*(occurrenceProb[randomNum]*y);
		//		System.out.println("[DEBUG] z0X = "+estimationX[0]);

		double ziX = 0;
		int current_tf = 0;
		int k = 1;
		double weightsSum = 0;
		double prob = 0;

		/****************Campionamento*****************/
		while(k < n){
			weightsSum = ak.getWeightsSum();

			//Valutazione della probabilità
			if(weightsSum == 0){
				prob = d + 0.1;
			} else{
				prob = Math.random();
				//				System.out.println("[DEBUG] valore di probabilità estratto: "+prob);
			}

			if (prob <= d){
//				System.out.println("[DEBUG] Ramo 1");
				//estrazione di un campione valutando il vettore dei pesi dell'active set
				current_tf = ak.testFrameExtraction(d);
				/****wr****/
				sck.add(current_tf);
				/****wr****/
				name = testFrame.get(current_tf).getTfID(); //nome univoco
				esito = testFrame.get(current_tf).extractAndExecuteTestCase();
				//				System.out.println("[DEBUG] il Test Frame selezionato è "+name+" con esito "+esito);

				//Calcolo della zi:
				//1. Calcolo della sommatoria
				ziX = 0;
				//2. Somma del valore campionato
				if(esito){
//					System.out.println("[DEBUG] qi: "+ak.qi);
//					ziX = ziX + occurrenceProb[current_tf]/ak.qi;
					/****wr****/
					for(int f=0; f<sck.size(); f++){
						ak.qiCalculation(d, sck.get(f));
						ziX= ziX + occurrenceProb[current_tf]/ak.qi;
					}
					/****wr****/
//					System.out.println("[DEBUG] qi: "+ak.qi);
					
					numfp++;
					tc = testFrame.get(current_tf).getReqType()+"\n "+testFrame.get(current_tf).getUrl()+"\n "+testFrame.get(current_tf).getSelPayload();
					this.failedRequest.add(tc);
				}
				
//				System.out.println("[DEBUG] z"+k+" =" + ziX);

//				System.out.println("[DEBUG] Active Set Update");
				//aggiunta del TF all'active set
				ak.activeSetUpdate(name , current_tf, esito, weightsMatrix);
//				System.out.println("[DEBUG] End Ramo 1");

			} else {
//				System.out.println("[DEBUG] Ramo 2");
				//selziono un campione random e ne prelevo l'id
				current_tf = ThreadLocalRandom.current().nextInt(0, testFrame.size());

				name = testFrame.get(current_tf).getTfID();
				esito = testFrame.get(current_tf).extractAndExecuteTestCase();
				//				System.out.println("[DEBUG] il Test Frame selezionato è "+name+" con esito "+esito);

				//Calcolo della zi:
				//1. Calcolo della sommatoria
				ziX = 0;
				//2. Somma del valore campionato
				if(esito){
					ak.qiCalculation(d, current_tf);
//					System.out.println("[DEBUG] qi: "+ak.qi);
//					ziX = ziX + occurrenceProb[current_tf]/ak.qi;
					/****wr****/
					for(int f=0; f<sck.size(); f++){
						ak.qiCalculation(d, sck.get(f));
						ziX= ziX + occurrenceProb[current_tf]/ak.qi;
					}
					/****wr****/
//					System.out.println("[DEBUG] qi: "+ak.qi);
					
					numfp++;
					tc = testFrame.get(current_tf).getReqType()+"\n "+testFrame.get(current_tf).getUrl()+"\n "+testFrame.get(current_tf).getSelPayload();
					this.failedRequest.add(tc);
				}

				//				System.out.println("[DEBUG] qi =" + ak.qi);	
//				System.out.println("[DEBUG] z"+k+" =" + ziX);

				ak.activeSetUpdate(name , current_tf, esito, weightsMatrix);
//				System.out.println("[DEBUG] End Ramo 1");
			}

			estimationX[k] = ziX;
			k++;
		}

		//		ak.printSelectedTestFrame();
		/***************Stima***************/
		this.z = estimationX;
		return this.estimatorBoCSP(n, estimationX);

	}

	public double[] selectAndRunTestCaseHH(int n, ArrayList<TestFrame> testFrame, double[][] weightsMatrix, double d){
		failedRequest.clear();
		numfp = 0;

		//Verifica dei dati in input
		if(n <= 0){
			double[] error =  {-1.0, -1.0};
			return error;
		}

		/**************Inizializzazione****************/
		//Definizione delle strutture dati: scompl, valori non ancora selezionati; occurrenceProb, vettore delle probabilità di occorrenza
		double[] occurrenceProb = new double[testFrame.size()];

		for(int i = 0; i < testFrame.size(); i++){
			occurrenceProb[i] = testFrame.get(i).getOccurrenceProb();
			//			System.out.println(occurrenceProb[i]);
		}

//		System.out.println("[DEBUG] Passo 0");

		//Selezione della prima osservazione mediante SRS
		int randomNum = ThreadLocalRandom.current().nextInt(0, testFrame.size());
		//		System.out.println("[DEBUG] Numero random estratto "+randomNum);

		//		Inizializzazione dell'ActiveSet
		ActiveSetWR ak = new ActiveSetWR(n, testFrame.size(), occurrenceProb);

		String name = testFrame.get(randomNum).getTfID();
		boolean esito = testFrame.get(randomNum).extractAndExecuteTestCase();
		String tc = testFrame.get(randomNum).getReqType()+"\n "+testFrame.get(randomNum).getUrl()+"\n "+testFrame.get(randomNum).getSelPayload();
		//		System.out.println("[DEBUG] il Test Frame selezionato è "+name+ " con esito " +esito);

		//aggiornamento dell'active set e dell'insime dei TF non ancora selezionati
		ak.qiCalculation(d, randomNum);
		ak.activeSetUpdate(name , randomNum, esito, weightsMatrix);

		double y = 0;
		//si suppone esito positivo (true) se viene rilevato un fallimento.
		if (esito) {
			y = 1;
			numfp++;
			this.failedRequest.add(tc);
		}

		//Definizione dell'array contenente le stime passo passo:
		double[] estimationX = new double[n];

		//calcolo del primo valore necessario per la stima (t).
		estimationX[0] = (testFrame.size())*(occurrenceProb[randomNum]*y);
		//		System.out.println("[DEBUG] z0X = "+estimationX[0]);

		double ziX = 0;
		int current_tf = 0;
		int k = 1;
		double weightsSum = 0;
		double prob = 0;

		/****************Campionamento*****************/
		while(k < n){
			weightsSum = ak.getWeightsSum();

			//Valutazione della probabilità
			if(weightsSum == 0){
				prob = d + 0.1;
			} else{
				prob = Math.random();
				//				System.out.println("[DEBUG] valore di probabilità estratto: "+prob);
			}

			if (prob <= d){
//				System.out.println("[DEBUG] Ramo 1");
				//estrazione di un campione valutando il vettore dei pesi dell'active set
				current_tf = ak.testFrameExtraction(d);
				name = testFrame.get(current_tf).getTfID(); //nome univoco
				esito = testFrame.get(current_tf).extractAndExecuteTestCase();
				//				System.out.println("[DEBUG] il Test Frame selezionato è "+name+" con esito "+esito);

				//Calcolo della zi:
				//1. Calcolo della sommatoria
				ziX = ak.getOutcomeSumX();
				//2. Somma del valore campionato
				if(esito){
					//					System.out.println("[DEBUG] qi: "+ak.qi);
					ziX = ziX + occurrenceProb[current_tf]/ak.qi;
					numfp++;
					tc = testFrame.get(current_tf).getReqType()+"\n "+testFrame.get(current_tf).getUrl()+"\n "+testFrame.get(current_tf).getSelPayload();
					this.failedRequest.add(tc);
				}
				
//				System.out.println("[DEBUG] z"+k+" =" + ziX);

//				System.out.println("[DEBUG] Active Set Update");
				//aggiunta del TF all'active set
				ak.activeSetUpdate(name , current_tf, esito, weightsMatrix);
//				System.out.println("[DEBUG] End Ramo 1");

			} else {
//				System.out.println("[DEBUG] Ramo 2");
				//selziono un campione random e ne prelevo l'id
				current_tf = ThreadLocalRandom.current().nextInt(0, testFrame.size());

				name = testFrame.get(current_tf).getTfID();
				esito = testFrame.get(current_tf).extractAndExecuteTestCase();
				//				System.out.println("[DEBUG] il Test Frame selezionato è "+name+" con esito "+esito);

				//Calcolo della zi:
				//1. Calcolo della sommatoria
				ziX = ak.getOutcomeSumX();
				//2. Somma del valore campionato
				if(esito){
					ak.qiCalculation(d, current_tf);
					ziX = ziX + (occurrenceProb[current_tf]/ak.qi);
					numfp++;
					tc = testFrame.get(current_tf).getReqType()+"\n "+testFrame.get(current_tf).getUrl()+"\n "+testFrame.get(current_tf).getSelPayload();
					this.failedRequest.add(tc);
				}

				//				System.out.println("[DEBUG] qi =" + ak.qi);	
//				System.out.println("[DEBUG] z"+k+" =" + ziX);

				ak.activeSetUpdate(name , current_tf, esito, weightsMatrix);
//				System.out.println("[DEBUG] End Ramo 1");
			}

			estimationX[k] = ziX/(k+1);
			k++;
		}

		//		ak.printSelectedTestFrame();
		/***************Stima***************/
		this.z = estimationX;
		return this.estimatorBoCSP(n, estimationX);

	}

	/**********************Estimator************************/
	//stiamtore per n0=1
	private double[] estimatorBoCSP(int n, double[] estimationX){
		double sumX = 0;

		//Calcolo della sommatoria degli zi necessaria per la stima, viene considerato anche il primo valore,
		//dato che si tratta di un singolo valore e quindi va moltiplicato per 1
		for(int i=0; i<n; i++){
			//			System.out.println("[DEBUG] "+(i)+") " + estimationX[i]);
			sumX = sumX + estimationX[i];
		}
		//		System.out.println("[DEBUG]la somma deli zi è" + sum);

		double[] stima = new double[2];

		//Calcolo della stima.
		stima[0] = (1/(double)(n))*sumX;

		//		Calcolo della varianza
		double num = 0;

		for(int i=1; i<n; i++){
			num = num + Math.pow((estimationX[i] - estimationX[0]), 2);
		}

		//		La stima della varianza del totale si ottiene come il prodotto di N quadro per la stima della varianza della media
		stima[1]= num/(double)(n*(n-1));


		return stima;
	}
}
