# -*- coding: utf-8 -*-
# version 2021.12.22
from os.path import exists
import sys
from flask import Flask, request, send_from_directory, render_template, Response
from flask_cors import CORS
import read as rd       #grab passthrough functions from main read file
import write as wr      #grab passthrough functions from main write file
import evc as evc
import pickle
from GivLUT import GivLUT
import os
import time
import datetime
import json
from settings import GiV_Settings

logger = GivLUT.logger

#set-up Flask details
giv_api = Flask(__name__)
CORS(giv_api)

#Proxy Read Functions

def requestcommand(command,payload):
    try:
        requests=[]
        if exists(GivLUT.writerequests):
            with open(GivLUT.writerequests,'rb') as inp:
                requests=pickle.load(inp)
        requests.append([command,payload])
        with open(GivLUT.writerequests,'wb') as outp:
            pickle.dump(requests, outp, pickle.HIGHEST_PROTOCOL)
    except:
        e=sys.exc_info()[0].__name__, os.path.basename(sys.exc_info()[2].tb_frame.f_code.co_filename), sys.exc_info()[2].tb_lineno
        logger.error ("Error in requesting control command: "+str(e))

def response(id: str):
    responses=[]
    starttime=datetime.datetime.now()
    while True:
        time.sleep(0.1)
        if exists(GivLUT.restresponse):
            with GivLUT.restlock:
                with open(GivLUT.restresponse,'r') as inp:
                    responses=json.load(inp)
                for response in responses[:]:
                    logger.debug("Response in file is: "+str(response))
                    if response['id']==id:
                        logger.debug("found REST response")
                        # remove item from responses
                        responses.remove(response)
                        with open(GivLUT.restresponse,'w') as outp:
                            outp.write(json.dumps(responses))
                        return response['result']            
        waittime=datetime.datetime.now()-starttime
        if waittime.total_seconds()>15:
            return "{'result':'Error: REST Command non-responsive'}"



@giv_api.route("/showdata")
def index():
    output=rd.getCache()
    return render_template('showdata.html', title="page", jsonfile=json.dumps(output))

@giv_api.route('/settings', methods=['POST'])
def savesetts():
    if exists("/config/GivTCP/allsettings.json"):
        SFILE="/config/GivTCP/allsettings.json"
    else:
        SFILE="/app/allsettings.json"
    setts = request.get_json()
    with open(SFILE, 'w') as f:
        f.write(json.dumps(setts,indent=4))
    return "Settings Updated"

@giv_api.route('/settings', methods=['GET'])
def returnsetts():
    if exists("/config/GivTCP/allsettings.json"):
        SFILE="/config/GivTCP/allsettings.json"
    else:
        SFILE="/app/allsettings.json"
    with open(SFILE, 'r') as f1:
        setts=json.load(f1)
        return setts

@giv_api.route('/runAll', methods=['GET'])
def getAll():
    # We need a safe way to do this for REST... just sending cache for now
    #logger.critical("runAll called via REST")
    output=rd.getCache()
    if output == None:
        return "{\"Result\":\"Error, no data available\"}"
    else:
        return output

@giv_api.route('/reboot', methods=['GET'])
def reboot():
    requestcommand("rebootinverter")
    return response("rebootinverter")

@giv_api.route('/restart', methods=['GET','POST'])
def restart():
    output=wr.rebootAddon()
    response=json.dumps({
        "data": {
            "result": "Container restarting..."
        }
    }),
    status=200,
    mimetype="application/json"
    return Response(response)

#Publish last cached Invertor Data
@giv_api.route('/readData', methods=['GET'])
def rdData():
    #logger.critical("readData called via REST")
    output=rd.getCache()
    if output == None:
        return "{\"Result\":\"Error, no data available\"}"
    else:
        return output

#Publish last cached Invertor Data
@giv_api.route('/getCache', methods=['GET'])
def gtCache():
    #logger.critical("getCache called via REST")
    output=rd.getCache()
    if output == None:
        return "{\"Result\":\"Error, no data available\"}"
    else:
        return output

# Read from Invertor put in cache
#@giv_api.route('/getData', methods=['GET'])
#def gtData():
#    return GivQueue.q.enqueue(rd.getData,True)

#Proxy Write Functions
@giv_api.route('/enableChargeTarget', methods=['POST'])
def enChargeTrgt():
    payload = request.get_json(silent=True, force=True)
    requestcommand("enableChargeTarget",payload)
    return response("setChargeTarget")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/enableChargeSchedule', methods=['POST'])
def enableChrgSchedule():
    payload = request.get_json(silent=True, force=True)
    requestcommand("enableChargeSchedule",payload)
    return response("enableChargeSchedule")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/enableDischargeSchedule', methods=['POST'])
def enableDischrgSchedule():
    payload = request.get_json(silent=True, force=True)
    requestcommand("enableDischargeSchedule",payload)
    return response("enableDischargeSchedule")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/enableDischarge', methods=['POST'])
def enableBatDisharge():
    payload = request.get_json(silent=True, force=True)
    requestcommand("enableDischarge",payload)
    return response("enableDischarge")
    #return {"result":"Control command sent: "+str(payload)}

### Should this include a slot number and use setChargeTarget2 ###

@giv_api.route('/setChargeTarget', methods=['POST'])
def setChrgTarget():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setChargeTarget",payload)
    return response("setChargeTarget")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setExportTarget', methods=['POST'])
def setExpTarget():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setExportTarget",payload)
    return response("setExportTarget")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDischargeTarget', methods=['POST'])
def setDischrgTarget():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setDischargeTarget",payload)
    return response("setDischargeTarget")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setBatteryReserve', methods=['POST'])
def setBattReserve():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setBatteryReserve",payload)
    return response("setBatteryReserve")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setChargeRate', methods=['POST'])
def setChrgeRate():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setChargeRate",payload)
    return response("setChargeRate")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setCarChargeBoost', methods=['POST'])
def setCarBoost():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setCarChargeBoost",payload)
    return response("setCarChargeBoost")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setExportLimit', methods=['POST'])
def setExpLim():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setExportLimit",payload)
    return response("setExportLimit")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDischargeRate', methods=['POST'])
def setDischrgeRate():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setDischargeRate",payload)
    return response("setDischargeRate")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setPauseSlot', methods=['POST'])
def setPausSlot():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setPauseSlot",payload)
    return response("setPauseSlot")
    #return {"result":"Control command sent: "+str(payload)}

### Should these now include a slot number as the input? ###

@giv_api.route('/setChargeSlot', methods=['POST'])
def setChrgSlot():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setChargeSlot",payload)
    return response("setChargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setChargeSlot1', methods=['POST'])
def setChrgSlot1():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=1
    requestcommand("setChargeSlot",payload)
    return response("setChargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setChargeSlot2', methods=['POST'])
def setChrgSlot2():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=2
    requestcommand("setChargeSlot",payload)
    return response("setChargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setChargeSlot3', methods=['POST'])
def setChrgSlot3():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=3
    requestcommand("setChargeSlot",payload)
    return response("setChargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDischargeSlot', methods=['POST'])
def setDischrgSlot():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setDischargeSlot",payload)
    return response("setDischargeSlot")

@giv_api.route('/setDischargeSlot1', methods=['POST'])
def setDischrgSlot1():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=1
    requestcommand("setDischargeSlot",payload)
    return response("setDischargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDischargeSlot2', methods=['POST'])
def setDischrgSlot2():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=2
    requestcommand("setDischargeSlot",payload)
    return response("setDischargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDischargeSlot3', methods=['POST'])
def setDischrgSlot3():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=3
    requestcommand("setDischargeSlot",payload)
    return response("setDischargeSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setExportSlot1', methods=['POST'])
def setExpSlot1():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=1
    requestcommand("setExportSlot",payload)
    return response("setExportSlot")
    #return {"result":"Control command sent: "+str(payload)}
@giv_api.route('/setExportSlot2', methods=['POST'])
def setExpSlot2():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=2
    requestcommand("setExportSlot",payload)
    return response("setExportSlot")
    #return {"result":"Control command sent: "+str(payload)}
@giv_api.route('/setExportSlot3', methods=['POST'])
def setExpSlot3():
    payload = request.get_json(silent=True, force=True)
    payload['slot']=3
    requestcommand("setExportSlot",payload)
    return response("setExportSlot")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/tempPauseDischarge', methods=['POST'])
def tmpPauseDischrg():
    payload = request.get_json(silent=True, force=True)
    if payload['duration'] == "Cancel" or payload['duration'] == "0":
        if exists(".tpdRunning"):
            jobid= str(open(".tpdRunning","r").readline().strip('\n'))
            logger.debug("Retrieved jobID to cancel Temp Pause Discharge: "+ str(jobid))
            requestcommand("cancelJob",jobid)
            return response("cancelJob")
        else:
            logger.error("Temp Pause Discharge is not currently running")
            return "{'result':'Error: Temp Pause Discharge is not currently running'}"
    else:
        requestcommand("tempPauseDischarge",int(payload['duration']))
        return response("tempPauseDischarge")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/tempPauseCharge', methods=['POST'])
def tmpPauseChrg():
    payload = request.get_json(silent=True, force=True)
    if payload['duration'] == "Cancel" or payload['duration'] == "0":
        if exists(".tpcRunning"):
            jobid= str(open(".tpcRunning","r").readline().strip('\n'))
            logger.info("Retrieved jobID to cancel Temp Pause Charge: "+ str(jobid))
            requestcommand("cancelJob",jobid)
            return response("cancelJob")
        else:
            logger.error("Temp Pause Charge is not currently running")
            return "{'result':'Error: Temp Pause Charge is not currently running'}"
    else:
        requestcommand("tempPauseCharge",int(payload['duration']))
        return response("tempPauseCharge")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/forceCharge', methods=['POST'])
def frceChrg():
    payload = request.get_json(silent=True, force=True)
    #Check if Cancel then return the right function
    if payload['duration'] == "Cancel" or payload['duration'] == "0":
        if exists(".FCRunning"):
            jobid= str(open(".FCRunning","r").readline()).strip('\n')
            logger.debug("Retrieved jobID to cancel Force Charge: "+ str(jobid))
            requestcommand("cancelJob",jobid)
            return response("cancelJob")
        else:
            logger.error("Force Charge is not currently running")
            return "{'result':'Error: Force Charge is not currently running'}"
    else:
        requestcommand("forceCharge",int(payload['duration']))
        return response("forceCharge")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/forceExport', methods=['POST'])
def frceExprt():
    payload = request.get_json(silent=True, force=True)
    if payload['duration'] == "Cancel" or payload['duration'] == "0":
        if exists(".FERunning"):
            jobid= str(open(".FERunning","r").readline()).strip('\n')
            logger.debug("Retrieved jobID to cancel Force Export: "+ str(jobid))
            requestcommand("cancelJob",jobid)
            return response("cancelJob")
        else:
            logger.error("Force Export is not currently running")
            return "{'result':'Error: Force Export is not currently running'}"
    else:
        requestcommand("forceExport",int(payload['duration']))
        return response("forceExport")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setBatteryMode', methods=['POST'])
def setBattMode():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setBatteryMode",payload)
    return response("setBatteryMode")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setBatteryPowerMode', methods=['POST'])
def setBattPwrMode():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setBatteryPowerMode",payload)
    return response("setBatteryPowerMode")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setBatteryPauseMode', methods=['POST'])
def setBattPausMode():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setBatteryPauseMode",payload)
    return response("setBatteryPauseMode")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setDateTime', methods=['POST'])
def setDate():
    payload = request.get_json(silent=True, force=True)
    requestcommand("setDateTime",payload)
    return response("setDateTime")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/switchRate', methods=['POST'])
def swRates():
    payload = request.get_json(silent=True, force=True)
    requestcommand("switchRate",payload['rate'])
    return response("switchRate")
    #return {"result":"Control command sent: "+str(payload)}

@giv_api.route('/setImportCap', methods=['POST'])
def impCap():
    payload = request.get_json(silent=True, force=True)
    return evc.setImportCap(payload)

@giv_api.route('/setCurrentLimit', methods=['POST'])
def currLimit():
    payload = request.get_json(silent=True, force=True)
    return evc.setCurrentLimit(payload)

@giv_api.route('/setChargeControl', methods=['POST'])
def chrgeControl():
    payload = request.get_json(silent=True, force=True)
    return evc.setChargeControl(payload)

@giv_api.route('/setChargeMode', methods=['POST'])
def chrgMode():
    payload = request.get_json(silent=True, force=True)
    return evc.setChargeMode(payload)

@giv_api.route('/setChargingMode', methods=['POST'])
def chrgingMode():
    payload = request.get_json(silent=True, force=True)
    return evc.setChargingMode(payload)

@giv_api.route('/setMaxSessionEnergy', methods=['POST'])
def maxSession():
    payload = request.get_json(silent=True, force=True)
    return evc.setMaxSessionEnergy(payload)

@giv_api.route('/getEVCCache', methods=['GET'])
def gtEVCChce():
    payload = request.get_json(silent=True, force=True)
    return evc.getEVCCache()



if __name__ == "__main__":
    giv_api.run()
