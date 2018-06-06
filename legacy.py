IS_MEASURE = 'is_measure'
TIME_start = 'time_start'
TIME_stop = 'time_stop'
WAS_MEASURE = 'was_measure'
WEIGHT_start = 'weight_start'
WEIGHT_stop = 'weight_stop'
#----------------------GPIO Setup and Assignment-------------------------------

#GPIO.setmode(GPIO.BCM)

#GPIO Assignment
PIN_PUMP_1 = 17
PIN_PUMP_2 = 27
PIN_Switch_Valve = 22
PIN_Drain_Valve = 18
PIN_Level_Scale_Up = 24
PIN_Level_Scale_Low = 25
PIN_Level_Const_Low = 5

#GPIO setup
# GPIO.setup(PIN_PUMP_1, GPIO.OUT)
# GPIO.setup(PIN_PUMP_2, GPIO.OUT)
# GPIO.setup(PIN_Switch_Valve, GPIO.OUT)  # Switch between Valves. Bypass Valve initially open!
# GPIO.setup(PIN_Drain_Valve, GPIO.OUT)
# GPIO.setup(PIN_Level_Scale_Up, GPIO.IN)
# GPIO.setup(PIN_Level_Scale_Low, GPIO.IN)
# GPIO.setup(PIN_Level_Const_Low, GPIO.IN)

#--------------------------------Open Serial Port----------------------------------------
# ser = serial.Serial()
# ser.port = '/dev/ttyS0'
# ser.baudrate = 9600
# ser.bytesize = serial.SEVENBITS
# ser.timeout = 1

#----------------------------Exceptions--------------------------------------------------
class Tank_Level_Error(Exception):
    pass
#----------------------------Functions and Procedures------------------------------------

def start_station():
    print('Starte Betrieb')
    predefine_gpios()
    start_pump1()
    time.sleep(t_fill_const)


def predefine_gpios():
    GPIO.output(PIN_PUMP_1, GPIO.LOW)
    GPIO.output(PIN_PUMP_2, GPIO.LOW)
    GPIO.output(PIN_Switch_Valve, GPIO.LOW) # Bypass Valve Open!
    GPIO.output(PIN_Drain_Valve, GPIO.LOW) #Drain closed


def new_measurement():
    reset_values()

    start_pump2()

    #  hier Drossel einstellen
    time.sleep(t_stabilize) # zur Stabilisierung der Stoemung nach dem Drosseln

    #get_weight()
    start_filling()

    #burst() # Vorgang zur Bestimmung von Messfehlern der Umschalteinrichtung (provisorisch)

    wait_for_full_tank()
    stop_filling()
    #get_weight()

    display_results()
    time.sleep(t_after)

    drain_weighting_tank()


def reset_values():
# Messwerte zuruecksetzen
    state = {
        IS_MEASURE: False,
        TIME_start: None,
        TIME_stop: None,
        WAS_MEASURE: False,
        WEIGHT_start: None,
        WEIGHT_stop: None
    }


def start_pump1():
    GPIO.output(PIN_PUMP_1, GPIO.HIGH)
    print('Pumpe 1 startet')


def start_pump2():
    if GPIO.input(PIN_Level_Const_Low) == GPIO.HIGH:
        GPIO.output(PIN_PUMP_2, GPIO.HIGH)
        print('Pumpe 2 startet')
    else:
        const_tank_low()


def start_filling():
    if not state[IS_MEASURE] and GPIO.input(PIN_Level_Scale_Up) != GPIO.HIGH:

        GPIO.output(PIN_Switch_Valve, GPIO.HIGH)
        time.sleep(0.075) # Kompensation Umschaltzeit
        state[TIME_start] = time.time()
        state[IS_MEASURE] = True
        state[WAS_MEASURE] = False
        print('Umgeschaltet - Waagenfass wird beladen')
    else:
        raise Exception


def wait_for_full_tank():

    GPIO.wait_for_edge(PIN_Level_Scale_Up, GPIO.RISING)
    print('Waagenfass voll gefuellt')

def stop_filling():
    if state[IS_MEASURE]:
        GPIO.output(PIN_Switch_Valve, GPIO.LOW)
        time.sleep(0.075)  # Kompensation Umschaltzeit
        state[TIME_stop] = time.time()
        state[IS_MEASURE] = False
        state[WAS_MEASURE] = True
        print('Umgeschaltet - Vorratsfass wird beladen')
    else:
        raise Exception


def display_results():
    delta_t = state[TIME_stop] - state[TIME_start]
    delta_m = state[WEIGHT_stop] - state[WEIGHT_start]
    m_dot = 1.00106*delta_m / delta_t       #Dichtekorrektur
    V_dot = m_dot / rho
    V_dot_lph = V_dot * 3600000
    print('Gemessene Werte')
    print('Datum'+time.strftime("%d.%m.%Y %H:%M:%S"))
    print('Messzeit: '+ str(delta_t)+ ' s')
    print ('Gewichtsdifferenz: '+ str(delta_m)+ ' Kg')
    print ('Massenstrom: ' + str(m_dot)+ 'Kg/s')
    print('grober Volumenstrom ' + str(V_dot) + 'Kg/m^3  oder ' + str(V_dot_lph) + ' l/h'  )

    # Ergebnisse in text abspeichern, provisorisch
    note = open("Messwerte.txt", "a")
    note.write(time.strftime("%d.%m.%Y %H:%M:%S")+'\n')
    note.write('Messzeit: ' + str(delta_t) + ' s\n')
    note.write('Gewichtsdifferenz: ' + str(delta_m) + ' Kg\n')
    note.write('Massenstrom: ' + str(m_dot) + 'Kg/s\n')
    note.write('grober Volumenstrom ' + str(V_dot) + 'Kg/m^3  oder ' + str(V_dot_lph) + ' l/h\n')
    note.write('  \n')
    note.close()


def drain_weighting_tank():
    GPIO.output(PIN_Drain_Valve, GPIO.HIGH)
    GPIO.output(PIN_PUMP_2, GPIO.LOW)
    print('Waagenfass wird entleert')
    print('Pumpe 2 gestoppt')
    if GPIO.input(PIN_Level_Scale_Low) == GPIO.HIGH:
        GPIO.wait_for_edge(PIN_Level_Scale_Low, GPIO.FALLING)
    time.sleep(20)
    GPIO.output(PIN_Drain_Valve, GPIO.LOW)
    print('Entleerung Abgeschlossen')


def const_tank_low():
    raise Tank_Level_Error('Fuellstand Konstant-Fass zu niedrig')


# def get_weight():
#     time.sleep(10)
#     print('Waegevorgang - bitte stillhalten')
#     ser.open()
#     while True:
#         line = ser.readline()  # Zeile einlesen
#         #print(line)
#         sline = line.split() # Zeile fuer Weiterverarbeitung auftrennen
#         if len(sline) == 3:      # Wenn stabil (Waage sendet Kg, Zeichen wenn stabil), dann Speicherung
#             print('Wert stabil')
#             result = ''.join(sline[:2])
#             break
#     print('Waegevorgang beendet')
#     print('Das gemessene Gewicht betraegt: '+ str(line))
#     if state[WAS_MEASURE] == False:
#         state[WEIGHT_start] = float(result)
#     else:
#         state[WEIGHT_stop] = float(result)
#     ser.close()


def turn_off():
    GPIO.output(PIN_Switch_Valve, GPIO.LOW)
    GPIO.output(PIN_PUMP_2, GPIO.LOW)
    GPIO.output(PIN_PUMP_1, GPIO.LOW)
    print('Pumpen ausgeschaltet')
    if GPIO.input(PIN_Level_Scale_Low) == GPIO.HIGH:
        drain_weighting_tank()
    print('Betrieb beendet')
    GPIO.cleanup()

def burst():
    i=0
    while True:
        i +=1
        time.sleep(1)
        stop_filling()
        #get_weight()
        print('Messzeit: '+str(state[TIME_stop]-state[TIME_start])+ '  '+str(i))
        time.sleep(4)
        start_filling()
        if i == 25:
            break
#---------------------------Default Values---------------------------------

t_fill_const = 70
t_stabilize = 25
t_after =20
t_timeout = 1000 # Einbinden!

#Angenommene Werte - Bei Einbindung weiterer Sensoren veraendern/ rausnehmen
rho = 997.05       # Dichte bei 25GradCelsius

# Tupel zur Messwerterfassung
state = {
    IS_MEASURE: False,  # findet Messung statt?
    TIME_start: None,  # Startzeit der Messung
    TIME_stop: None,  # Endzeit der Messung
    WAS_MEASURE: False,  # fand Messung schon statt?
    WEIGHT_start: None,  # Startgewicht
    WEIGHT_stop: None  # Endgewicht
}


# -------------------------General procedure-------------------------------
# def main():
#     try:
#         start_station()
#
#         new_measurement()
#
#         #Ende oder neue Messung
#
#     except Tank_Level_Error as ex:
#         print(ex)
#     except KeyboardInterrupt:
#         print('Stopped by user.')
#     except Exception:
#         print('Unknown error.')
#         raise
#
#     turn_off()