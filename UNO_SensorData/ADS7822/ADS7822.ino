#include <Arduino.h> 
#include <stdint.h>          // 数据类型定义
#include "UserInterface.h"
//定义引脚
const int s0 = 2;
const int s1 = 3;
const int s2 = 4;
const int s3 = 5;
const int EN = 6;
const int CS = 8;
const int DOUT = 9;
const int DCLK = 10;
//声明函数
void ChooseChannel(int channel);// 用来选择通道，输入通道号
float get_code(int x);//用来获得数据
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  //引脚模式
  pinMode(CS, OUTPUT);
  pinMode(DCLK, OUTPUT);
  pinMode(DOUT, INPUT);
  pinMode(EN, OUTPUT);
  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);
  pinMode(s3, OUTPUT);
  //引脚使能
  digitalWrite(EN, LOW);
  digitalWrite(CS, HIGH);
}

void loop() {
    //定义变量
    int num = 6;//电阻个数
    //电压测量
    float Voltage;
    float voltage_rec[5];
    float Voltage_mean;
    //扫描测量
    for(int j=0;j<num;j++){
      /*选定电阻*/
      ChooseChannel(j);
      delay(10);
      /*测量电阻*/
      Voltage_mean = 0.0;
      for(int i=0;i<5;i++){
          Voltage = get_code(15);
          voltage_rec[i] = Voltage;
          Voltage_mean=Voltage_mean+Voltage;
        }
        Voltage_mean = Voltage_mean/5;
        Serial.println(Voltage_mean);
    }
    Serial.println("e");
}

float get_code(int x){
  
  uint16_t byte_rec = 0;
  float voltage;
//  Serial.println("*************************串口数据采样************************");
  digitalWrite(DCLK, LOW);
  digitalWrite(CS, LOW);
  delayMicroseconds(5);
  for(int bit_ctr=0;bit_ctr<x;bit_ctr++){
    byte_rec = (byte_rec<<1);
    digitalWrite(DCLK, HIGH);
    delayMicroseconds(5);
//    Serial.print(digitalRead(DOUT));
//    Serial.print(" ");
    if (digitalRead(DOUT)==1){
      byte_rec = byte_rec|0x0001;
      }
    digitalWrite(DCLK, LOW);
    delayMicroseconds(5);
    }
//   Serial.print("\n");
   digitalWrite(DCLK, HIGH);
   digitalWrite(CS, HIGH);
   byte_rec = byte_rec&0x0FFF;
//   Serial.println("*************************采样电压转换**************************");
//   Serial.println(byte_rec);
//   Serial.println(byte_rec,BIN);
   voltage = byte_rec*5.12/4095;
   return voltage;
   
  }
void ChooseChannel(int channel)
{
  int controlPin[] = {s0, s1, s2, s3};

  int muxChannel[16][4] =
  {
    {0, 0, 0, 0}, //channel 0
    {1, 0, 0, 0}, //channel 1
    {0, 1, 0, 0}, //channel 2
    {1, 1, 0, 0}, //channel 3
    {0, 0, 1, 0}, //channel 4
    {1, 0, 1, 0}, //channel 5
    {0, 1, 1, 0}, //channel 6
    {1, 1, 1, 0}, //channel 7
    {0, 0, 0, 1}, //channel 8
    {1, 0, 0, 1}, //channel 9
    {0, 1, 0, 1}, //channel 10
    {1, 1, 0, 1}, //channel 11
    {0, 0, 1, 1}, //channel 12
    {1, 0, 1, 1}, //channel 13
    {0, 1, 1, 1}, //channel 14
    {1, 1, 1, 1} //channel 15
  };

  //给引脚赋值
  for (int i = 0; i < 4; i ++)
  {
    digitalWrite(controlPin[i], muxChannel[channel][i]);
  }  
}
