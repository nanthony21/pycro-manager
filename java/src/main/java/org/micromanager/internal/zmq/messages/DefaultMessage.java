/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.micromanager.internal.zmq.messages;

import java.lang.reflect.Field;
import java.util.Iterator;
import java.util.List;
import mmcorej.org.json.JSONException;
import mmcorej.org.json.JSONObject;

/**
 *
 * @author Nick Anthony <nickmanthony at hotmail.com>
 */
public abstract class DefaultMessage implements Message {
    static String MSG_TYPE = "msgType";
    
    public JSONObject toJson() throws JSONException {
        JSONObject obj = this.getMessageContents();
        obj.put(MSG_TYPE, this.getClass().getName());
        return obj;
    }
    
    public JSONObject getMessageContents() throws JSONException {
        JSONObject json = new JSONObject();
        try {
            for (Field field : this.getFields()) {
                json.put(field.getName(), field.get(this));
            }
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        }
        return json;
    }
    
    public abstract List<Field> getFields();
}