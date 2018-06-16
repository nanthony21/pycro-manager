package main.java.org.micromanager.plugins.magellan.channels;

import java.awt.Color;
import java.util.ArrayList;
import main.java.org.micromanager.plugins.magellan.demo.DemoModeImageData;
import main.java.org.micromanager.plugins.magellan.main.Magellan;
import main.java.org.micromanager.plugins.magellan.misc.GlobalSettings;
import mmcorej.StrVector;

/**
 * Class to encapsulate a bunch of ChannelsSettings. Should be owned by a specific acquisition settings object 
 * @author Henry
 */
public class ChannelSpec {
    
    private ArrayList<ChannelSetting> channels_;
    
    public ChannelSpec(String channelGroup) {
        updateChannelGroup(channelGroup);
    }
    
    public void updateChannelGroup(String channelGroup) {
        if (channels_ != null && channels_.size() != 0 && channels_.get(0).equals(channelGroup) ) {
            //nothing to update
            return;
        } 
        //The channel group for this object has been 
        int numCamChannels = (int) (GlobalSettings.getInstance().getDemoMode() ? DemoModeImageData.getNumChannels() : Magellan.getCore().getNumberOfCameraChannels());
        channels_ = new ArrayList<ChannelSetting>();
        if (numCamChannels <= 1) {
            for (String config : getChannelConfigs(channelGroup)) {
                channels_.add(new ChannelSetting(channelGroup, channelGroup == null || channelGroup.equals("") ? null : config, config, true));
            }
        } else { //multichannel camera
            for (int i = 0; i < numCamChannels; i++) {
                String cameraChannelName = Magellan.getCore().getCameraChannelName(i);
                if (getChannelConfigs(channelGroup).length == 0 || channelGroup == null || channelGroup.isEmpty()) {
                    channels_.add(new ChannelSetting(channelGroup, null, cameraChannelName, i == 0));
                } else {
                    for (String config : getChannelConfigs(channelGroup)) {
                        channels_.add(new ChannelSetting(channelGroup, config, cameraChannelName + "-" + config, i == 0));
                    }
                }
            }
        }
    }
    
    public void setUseOnAll(boolean use) {
        for (ChannelSetting c : channels_) {
         c.use_ = use;
        }
    }

    public void synchronizeExposures() {
        double e = channels_.get(0).exposure_;
        for (ChannelSetting c : channels_) {
            c.exposure_ = e;
        }
    }
    
    public boolean anyActive() {
        for (ChannelSetting c : channels_) {
         if (c.use_) {
            return true;
         }
      }
      return false;
    }
    
    public int getNumActiveChannels() {
         int count = 0;
        for (ChannelSetting c : channels_) {
            count += c.use_ ? 1 : 0;
        }
        return count; 
    }
    
    public String[] getActiveChannelNames() {
        String[] channelNames = new String[getNumActiveChannels()];
        for (int i = 0; i < channelNames.length; i++) {
            channelNames[i] = getActiveChannelSetting(i).name_;
        }
        return channelNames;
    }
    
      public String[] getAllChannelNames() {
        String[] channelNames = new String[channels_.size()];
        for (int i = 0; i < channelNames.length; i++) {
            channelNames[i] = channels_.get(i).name_;
        }
        return channelNames;
    }
    
      public Color[] getActiveChannelColors() {
        Color[] channelColors = new Color[getNumActiveChannels()];
        for (int i = 0; i < channelColors.length; i++) {
            channelColors[i] = getActiveChannelSetting(i).color_;
        }
        return channelColors;
    }

    public int getNumChannels() {
        return channels_.size();
    }
    
    public ChannelSetting getActiveChannelSetting(int i) {
        for (ChannelSetting c : channels_) {
            if (i == 0 && c.use_) {
                return c;
            }
            if (c.use_) {
                i--;
            }
        }
        throw new RuntimeException();
    }
    
    public ChannelSetting getChannelSetting(int i) {
        return channels_.get(i);
    }
    
    public void storeCurrentSettingsInPrefs() {        
      for (ChannelSetting c : channels_) {
          c.storeChannelInfoInPrefs();
      }
    }
    
    private static String[] getChannelConfigs(String channelGroup) {
      if (channelGroup == null || channelGroup.equals("")) {
         return new String[]{"Default"};
      }
      StrVector configs = Magellan.getCore().getAvailableConfigs(channelGroup);
      String[] names = new String[(int) configs.size()];
      for (int i = 0; i < names.length; i++) {
         names[i] = configs.get(i);
      }
      return names;
   }
}