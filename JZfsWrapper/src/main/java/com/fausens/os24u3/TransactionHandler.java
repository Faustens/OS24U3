package com.fausens.os24u3;

import java.io.File;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;

public class TransactionHandler {
    private HashMap<File,String> fileTransactionMap;
    private final String UUID;
    private final String ADDRESS = "http://127.0.0.1:5000";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    public TransactionHandler() {
        UUID = "Temp";
        fileTransactionMap = new HashMap<>();
        // 
    }

    public File openFile(String path) {
        File file = null;
        
        return file;
    }

    public void commitFile(File file) {}

    public void cancelFile(File file) {}

    public void createFile(String path) {}

    public void deleteFile(String path) {}

    public void createPath(String path) {}

    public void deletePath(String path) {}

    @Override
    protected void finalize() throws Throwable {
        // Degergister logic on Object destruction
    }

// ==================================================================
// API Interaction
// ==================================================================
    private String sendGetRequest(String target) throws Exception {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(ADDRESS+target))
            .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        String responseBody = response.body();
        return responseBody;
    }
    private String sendPostRequest(String target, String jsonPayloadString) throws Exception{
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(ADDRESS+target))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayloadString))
            .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        String responseBody = response.body();
        return responseBody;
    }

    private HashMap<String,String> parseJsonString(String jsonString) {
        jsonString = jsonString.trim();
        if (jsonString.startsWith("{") && jsonString.endsWith("}")) {
            jsonString = jsonString.substring(1,jsonString.length()-1);
        }
        HashMap<String,String> map = new HashMap<>();
        String[] pairs = jsonString.split(",");
        for (String pair : pairs) {
            pair = pair.trim();
            String[] keyValue = pair.split(":");
            String key = keyValue[0];
            String value = keyValue[1];
            map.put(key,value);
        }
        return map;
    }
    private String mapToJsonString(HashMap<String,String> map) {
        StringBuilder jsonStringBuilder = new StringBuilder();
        jsonStringBuilder.append("{");
        for (Map.Entry<String,String> entry : map.entrySet()) {
            jsonStringBuilder.append("\"").append(entry.getKey()).append("\":");
            jsonStringBuilder.append("\"").append(entry.getValue()).append("\",");
        }
        int length = jsonStringBuilder.length();
        if (length > 2) jsonStringBuilder.setLength(length-2);
        jsonStringBuilder.append("}");
        return jsonStringBuilder.toString();
    }

    private String registerRequest() throws Exception {
        String response = sendGetRequest("/register");
        Map<String,String> jsonMap = parseJsonString(response);
        String uuid = jsonMap.get("uuid");
        return uuid;
    }
    private void deregisterRequest(String uuid) throws Exception {
        try {
            String requestString = "{\"uuid\":\""+uuid+"\"}";
            sendPostRequest("/deregister", requestString);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void openFileRequest() {}
    private void commitFileRequest() {}
    private void cancelFileRequest() {}
    private void createFileRequest() {}
    private void deleteFileRequest() {}

    private void createPathRequest() {}
    private void removePathRequest() {}

// ==================================================================
// Class: Transaction
// ==================================================================
    private class Transaction {

    }
}