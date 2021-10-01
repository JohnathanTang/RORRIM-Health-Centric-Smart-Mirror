
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"


Adafruit_MLX90614 mlx = Adafruit_MLX90614();
MAX30105 particleSensor;

#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
//Arduino Uno doesn't have enough SRAM to store 50 samples of IR led data and red led data in 32-bit format
//To solve this problem, 16-bit MSB of the sampled data will be truncated. Samples become 16-bit data.
uint16_t irBuffer[50]; //infrared LED sensor data
uint16_t redBuffer[50];  //red LED sensor data
#else
uint32_t irBuffer[50]; //infrared LED sensor data
uint32_t redBuffer[50];  //red LED sensor data
#endif

int32_t heartRate; //heart rate value
int8_t validHeartRate;

int32_t spo2; //SPO2 value
int8_t validSPO2; //indicator to show if the SPO2 calculation is valid

 
boolean newData = false; 
char receivedChar; 

void setup(){
  Serial.begin(9600);
  //Serial.println("Adafruit MLX90614 Test");
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println(F("MAX30105 was not found. Please check wiring/power."));
    while (1);
  }

  particleSensor.setup(55, 4, 2, 200, 411, 4096); //Configure sensor with these settings
  
  if(!mlx.begin())
  {
    Serial.println(F("MLX90614 was not found. Please check wiring/power."));
    while(1);
  }
//
   for (byte i = 0 ; i < 50 ; i++)
   {
    while (particleSensor.available() == false) //do we have new data?
      particleSensor.check(); //Check the sensor for new data

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample(); //We're finished with this sample so move to next sample
   }
   maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
}

void get_spo2(){
  for (byte i = 25; i < 50; i++)
    {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }

    //take 25 sets of samples before calculating the heart rate.
    for (byte i = 25; i < 50; i++)
    {
      while (particleSensor.available() == false) //do we have new data?
        particleSensor.check(); //Check the sensor for new data

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample(); //We're finished with this sample so move to next sample
      delay(100); 
    }


    
    if(!validSPO2){
      //Serial.println("SPO2 not valid. Trying again..."); 
      maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
      get_spo2();
    }else{
      //Serial.print(F("SPO2 = "));
      Serial.println(spo2, DEC);
      maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
    }
}

void obj_tempF(){
   double sum_temp = 0;
    for(int i = 0; i < 5; i++) {
        sum_temp += mlx.readObjectTempF();
        delay(1000);
    }
    Serial.println(sum_temp/5);
}

void amb_tempF(){
   double sum_temp = 0;
    for(int i = 0; i < 5; i++) {
        sum_temp += mlx.readAmbientTempF();
        delay(1000);
    }
    Serial.println(sum_temp/5);
}

void amb_tempC(){
   double sum_temp = 0;
    for(int i = 0; i < 5; i++) {
        sum_temp += mlx.readAmbientTempC();
        delay(1000);
    }
    Serial.println(sum_temp/5);
}

void obj_tempC(){
   double sum_temp = 0;
    for(int i = 0; i < 5; i++) {
        sum_temp += mlx.readObjectTempC();
        delay(1000);
    }
    Serial.println(sum_temp/5);
}

void spo2_objtempF(){
  double sum_temp = 0;
  for (byte i = 25; i < 50; i++)
    {
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25] = irBuffer[i];
    }

    //take 25 sets of samples before calculating the heart rate.
    for (byte i = 25; i < 50; i++)
    {
      while (particleSensor.available() == false) //do we have new data?
        particleSensor.check(); //Check the sensor for new data

      redBuffer[i] = particleSensor.getRed();
      irBuffer[i] = particleSensor.getIR();
      particleSensor.nextSample(); //We're finished with this sample so move to next sample
      sum_temp += mlx.readObjectTempF();
      delay(100); 
    }
    
    if(!validSPO2){
      //Serial.println("SPO2 not valid. Trying again..."); 
      maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
      spo2_objtempF();
    }else{
      
      //Serial.print(F("SPO2 = "));
      Serial.print(spo2,DEC);
      Serial.print(" ");
      Serial.println(sum_temp/25); 
      maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
      
    }
}

void loop() {
    if (Serial.available() > 0) {
        int recv = (Serial.read() - '0');  
            switch (recv) {
                case 0:  amb_tempC();break;
                case 1:  obj_tempC();break;
                case 2:  amb_tempF();break;
                case 3:  obj_tempF();break; 
                case 4:  get_spo2(); break;
                case 5:  spo2_objtempF(); break;
                default: break;
            }
        }
  }






//
//#include <Wire.h> //include Wire.h library
//
//void setup()
//{
//  Wire.begin(); // Wire communication begin
//  Serial.begin(9600); // The baudrate of Serial monitor is set in 9600
//  while (!Serial); // Waiting for Serial Monitor
//  Serial.println("\nI2C Scanner");
//}
//
//void loop()
//{
//  byte error, address; //variable for error and I2C address
//  int nDevices;
//
//  Serial.println("Scanning...");
//
//  nDevices = 0;
//  for (address = 1; address < 127; address++ )
//  {
//    // The i2c_scanner uses the return value of
//    // the Write.endTransmisstion to see if
//    // a device did acknowledge to the address.
//    Wire.beginTransmission(address);
//    error = Wire.endTransmission();
//
//    if (error == 0)
//    {
//      Serial.print("I2C device found at address 0x");
//      if (address < 16)
//        Serial.print("0");
//      Serial.print(address, HEX);
//      Serial.println("  !");
//      nDevices++;
//    }
//    else if (error == 4)
//    {
//      Serial.print("Unknown error at address 0x");
//      if (address < 16)
//        Serial.print("0");
//      Serial.println(address, HEX);
//    }
//  }
//  if (nDevices == 0)
//    Serial.println("No I2C devices found\n");
//  else
//    Serial.println("done\n");
//
//  delay(5000); // wait 5 seconds for the next I2C scan
//}
