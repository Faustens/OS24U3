package com.faustens.os24u3;

import java.util.HashMap;
import java.util.Map;

public class JsonParser {
    public JsonParser() {}

    public static HashMap<String,String> parseJsonString(String jsonString) {
        jsonString = jsonString.trim();
        if (jsonString.startsWith("{") && jsonString.endsWith("}")) {
            jsonString = jsonString.substring(1,jsonString.length()-1);
        }
        HashMap<String,String> map = new HashMap<>();
        String[] pairs = jsonString.split(",");
        for (String pair : pairs) {
            pair = pair.trim();
            String[] keyValue = pair.split(":");
            String key = keyValue[0].replace("\"","").trim();
            String value = keyValue[1].replace("\"","").trim();
            map.put(key,value);
        }
        return map;
    }
    public static String mapToJsonString(HashMap<String,String> map) {
        StringBuilder jsonStringBuilder = new StringBuilder();
        jsonStringBuilder.append("{");
        for (Map.Entry<String,String> entry : map.entrySet()) {
            jsonStringBuilder.append("\"").append(entry.getKey()).append("\":");
            jsonStringBuilder.append("\"").append(entry.getValue()).append("\",");
        }
        int length = jsonStringBuilder.length();
        if (length > 2) jsonStringBuilder.setLength(length-1);
        jsonStringBuilder.append("}");
        return jsonStringBuilder.toString();
    }

    public static String getJsonString(String... args) {
        if (args.length%2 != 0) return null;
        StringBuilder jsonStringBuilder = new StringBuilder();
        jsonStringBuilder.append("{");
        for (int i = 0; i < args.length/2; i++) {
            jsonStringBuilder.append("\"").append(args[i*2]).append("\":");
            jsonStringBuilder.append("\"").append(args[i*2+1]).append("\",");
        }
        int length = jsonStringBuilder.length();
        if (length > 2) jsonStringBuilder.setLength(length-1);
        jsonStringBuilder.append("}");
        return jsonStringBuilder.toString();
    }
}
