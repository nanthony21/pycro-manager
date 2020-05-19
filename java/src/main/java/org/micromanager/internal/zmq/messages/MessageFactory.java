/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.micromanager.internal.zmq.messages;

import java.util.ArrayList;
import java.util.List;
import mmcorej.org.json.JSONException;
import mmcorej.org.json.JSONObject;

/**
 *
 * @author Nick Anthony <nickmanthony at hotmail.com>
 */
public class MessageFactory {
    static String MSG_TYPE = "msgType";
    public enum Types {
        COMMAND,
        CLASSDEF,
        NEWCONNECTION;
    }
    
    public static Class<? extends DefaultMessage> getClass(Types type) {
        switch (type) {
            case COMMAND:
                return CommandMessage.class;
            case CLASSDEF:
                return ClassDefMessage.class;
            case NEWCONNECTION:
                return NewConnectionMessage.class;
        }
        throw new RuntimeException("A case was not handled.");
    }
    
    public static List<String> getFieldNames(Types type) {
        List<String> names = new ArrayList<>();
        switch (type) {
            case COMMAND:
                names.add("command");
                break;
            case CLASSDEF:
                names.add("api");
                break;
            case NEWCONNECTION:
                break;
        }
        return names;
    }
    
    public static DefaultMessage fromJson(JSONObject json) throws JSONException {
        try {
            for (Types type : Types.values()) {
                if (json.get(MSG_TYPE).equals(getClass(type))) {
                    Class<? extends DefaultMessage> msgClass = getClass(type);
                    DefaultMessage msg = msgClass.newInstance();
                    for (String fieldName : getFieldNames(type)) {
                       msgClass.getField(fieldName).set(msg, json.get(fieldName));
                    }
                    return msg;
                }
            }
        } catch (InstantiationException | IllegalAccessException | NoSuchFieldException e) {
            throw new RuntimeException(e);
        }
        throw new RuntimeException("No valid class found");
    }
}
