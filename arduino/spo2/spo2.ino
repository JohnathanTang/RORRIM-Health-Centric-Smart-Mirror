///* This code works with MAX30102 + 128x32 OLED i2c + Buzzer and Arduino UNO
// * It's displays the Average BPM on the screen, with an animation and a buzzer sound
// * everytime a heart pulse is detected
// * It's a modified version of the HeartRate library example
// * Refer to www.surtrtech.com for more details or SurtrTech YouTube channel
// */
//
//
//#include <Wire.h>
//#include "MAX30105.h"           //MAX3010x library
//#include "heartRate.h"          //Heart rate calculating algorithm
//
//MAX30105 particleSensor;
//
//const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
//byte rates[RATE_SIZE]; //Array of heart rates
//byte rateSpot = 0;
//long lastBeat = 0; //Time at which the last beat occurred
//float beatsPerMinute;
//int beatAvg;
//
////#define SCREEN_WIDTH 128 // OLED display width, in pixels
////#define SCREEN_HEIGHT 32 // OLED display height, in pixels
////#define OLED_RESET    -1 // Reset pin # (or -1 if sharing Arduino reset pin)
//
////Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); //Declaring the display name (display)
//
//
//
//void setup() {  
//  Serial.begin(9600);
//  delay(100);
//  //display.begin(SSD1306_SWITCHCAPVCC, 0x3C); //Start the OLED display
//  //display.display();
//  //delay(3000);
//  // Initialize sensor
//  particleSensor.begin(Wire, I2C_SPEED_FAST); //Use default I2C port, 400kHz speed
//  particleSensor.setup(); //Configure sensor with default settings
// // particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
//}
//
//void loop() {
// long irValue = particleSensor.getIR();    //Reading the IR value it will permit us to know if there's a finger on the sensor or not
// if(irValue > 7000){                                           //If a finger is detected
////    display.clearDisplay();                                   //Clear the display
////    display.drawBitmap(5, 5, logo2_bmp, 24, 21, WHITE);       //Draw the first bmp picture (little heart)
////    display.setTextSize(2);                                   //Near it display the average BPM you can display the BPM if you want
////    display.setTextColor(WHITE); 
////    display.setCursor(50,0); 
//    Serial.print(beatAvg);                
//    Serial.println( "BPM");             
////    display.setCursor(50,18);                
//    
////    display.display();
//    
//  if (checkForBeat(irValue) == true)                        //If a heart beat is detected
//  {
////    display.clearDisplay();                                //Clear the display
////    display.drawBitmap(0, 0, logo3_bmp, 32, 32, WHITE);    //Draw the second picture (bigger heart)
////    display.setTextSize(2);                                //And still displays the average BPM
////    display.setTextColor(WHITE);             
////    display.setCursor(50,0); 
//    Serial.print(beatAvg);                
//    Serial.println(" BPM");             
////    display.setCursor(50,18);                
//    
//    delay(100);
//    //We sensed a beat!
//    long delta = millis() - lastBeat;                   //Measure duration between two beats
//    lastBeat = millis();
//
//    beatsPerMinute = 60 / (delta / 1000.0);           //Calculating the BPM
//
//    if (beatsPerMinute < 255 && beatsPerMinute > 20)               //To calculate the average we strore some values (4) then do some math to calculate the average
//    {
//      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
//      rateSpot %= RATE_SIZE; //Wrap variable
//
//      //Take average of readings
//      beatAvg = 0;
//      for (byte x = 0 ; x < RATE_SIZE ; x++)
//        beatAvg += rates[x];
//      beatAvg /= RATE_SIZE;
//    }
//  }
//
//}
//  if (irValue < 7000){       //If no finger is detected it inform the user and put the average BPM to 0 or it will be stored for the next measure
//     beatAvg=0;               
//     Serial.println("Please Place Your Finger"); 
//     
//     }
//
//}










/*
  Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected
 
  The MAX30105 Breakout can handle 5V or 3.3V I2C logic. We recommend powering the board with 5V
  but it will also run at 3.3V.
*/

#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"


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


void setup()
{
  Serial.begin(9600); // initialize serial communication at 115200 bits per second:

  

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println(F("MAX30105 was not found. Please check wiring/power."));
    while (1);
  }

  particleSensor.setup(55, 4, 2, 200, 411, 4096); //Configure sensor with these settings
}

void loop()
{

  //read the first 50 samples, and determine the signal range
  for (byte i = 0 ; i < 50 ; i++)
  {
    while (particleSensor.available() == false) //do we have new data?
      particleSensor.check(); //Check the sensor for new data

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample(); //We're finished with this sample so move to next sample
//    Serial.print(F("red="));
//    Serial.print(redBuffer[i], DEC);
//    Serial.print(F(", ir="));
//    Serial.println(irBuffer[i], DEC);
  }

  //calculate heart rate and SpO2 after first 50 samples (first 4 seconds of samples)
  maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);

  //Continuously taking samples from MAX30102.  Heart rate and SpO2 are calculated every 1 second
  while (1)
  {
    //dumping the first 25 sets of samples in the memory and shift the last 25 sets of samples to the top
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
//      Serial.print(F("red="));
//      Serial.print(redBuffer[i], DEC);
//      Serial.print(F(", ir="));
//      Serial.print(irBuffer[i], DEC);
//
//      Serial.print(F(", HR="));
//      Serial.println(heartRate, DEC);

//      Serial.print(F(", HRvalid="));
//      Serial.print(validHeartRate, DEC);
      if(validSPO2){
        Serial.print(F(", SPO2="));
        Serial.println(spo2, DEC);
      }

//      Serial.print(F(", SPO2Valid="));
//      Serial.println(validSPO2, DEC);
      
    }

    //After gathering 25 new samples recalculate HR and SP02
    maxim_heart_rate_and_oxygen_saturation(irBuffer, 50, redBuffer, &spo2, &validSPO2, &heartRate, &validHeartRate);
  }
}
