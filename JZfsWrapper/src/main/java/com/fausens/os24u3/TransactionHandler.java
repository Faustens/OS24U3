package com.fausens.os24u3;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.InterruptedException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;

import com.fausens.os24u3.exceptions.*;

public class TransactionHandler {
    private HashMap<File,String> fileTransactionMap;
    private final String UUID;
    private final String ADDRESS = "http://127.0.0.1:5000";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    private TransactionHandler() throws Exception {
        UUID = register();
        if (UUID == null) throw new Exception();
        fileTransactionMap = new HashMap<>();
    }

    public static TransactionHandler newTransactionHandler() {
        try {
            return new TransactionHandler();
        } catch (Exception e) {
            return null;
        }
    }

    public void close() {
        deregister();
    }
// ============================================================================
// Filemanagement Methods
// ============================================================================
    private String register() {
        String uuid = null;
        try {
            uuid = sendGetRequest("/register").get("uuid");
        } catch (Exception e) {}
        return uuid;
    }
    private void deregister() {
        String requestString = JsonParser.getJsonString("uuid",UUID);
        try {
            // Response content doesn't really matter, either the uuid is there and can be deleted
            // or the problem is beyond this program's capabilities anyway.
            sendPostRequest("/deregister", requestString); 
        } catch (Exception e) {}
    }

    public File openFile(String path) throws IOException, FileNotFoundException, PathNotManagedException, Exception {
        String request = JsonParser.getJsonString("uuid",UUID,"path",path);
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/open_file",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200":
                String tid = responseMap.get("tid");
                String filepath = responseMap.get("copy_path");
                File file = new File(URI.create(filepath));
                fileTransactionMap.put(file,tid);
                return file;
            case "500": throw new Exception();
            case "403": throw new FileNotFoundException();
            case "407": throw new PathNotManagedException("Path not managed");
            default: throw new Exception();
        }
    }

    public boolean commitFile(File file) throws IOException, TransactionInvalidException, Exception{
        String request = JsonParser.getJsonString("tid",fileTransactionMap.get(file));
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/commit_file",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200": 
                fileTransactionMap.remove(file);
                return true;
            case "500": throw new Exception();
            case "402": throw new TransactionInvalidException("Transaction is either invalid or has never existed");
            default: throw new Exception();
        }
    }

    public boolean cancelFile(File file) throws IOException, Exception {
        String request = JsonParser.getJsonString("tid",fileTransactionMap.get(file));
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/close_file",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200":
                fileTransactionMap.remove(file);
                return true;
            case "500": throw new Exception();
            default: throw new Exception();
        }
    }

    public boolean createFile(String path) 
        throws IOException, 
            PathNotManagedException, 
            PathNotFoundException,
            FileNotFoundException,
            Exception 
    {
        String request = JsonParser.getJsonString("uuid",UUID,"path",path);
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/make_file",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200": return true;
            case "500": throw new Exception();
            case "403": throw new FileNotFoundException();
            case "405": throw new PathNotFoundException("Provided path does not exist");
            case "407": throw new PathNotManagedException("Path not managed");
            default: throw new Exception();
        }
    }

    public boolean deleteFile(String path) 
        throws IOException,
            PathNotManagedException,
            FileNotFoundException,
            Exception
    {
        String request = JsonParser.getJsonString("uuid",UUID,"path",path);
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/delete_file",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200": return true;
            case "500": throw new Exception();
            case "403": throw new FileNotFoundException();
            case "407": throw new PathNotManagedException("Path not managed");
            default: throw new Exception();
        }
    }

    public boolean createDirectory(String path)
        throws IOException, 
            PathNotManagedException,
            PathExistsException,
            Exception 
    {
        String request = JsonParser.getJsonString("uuid",UUID,"path",path);
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/make_directory",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200": return true;
            case "500": throw new Exception();
            case "406": throw new PathExistsException("Prived path already exists");
            case "407": throw new PathNotManagedException("Path not managed");
            default: throw new Exception();
        }
    }

    public boolean deleteDirectory(String path)
        throws IOException, 
            PathNotManagedException, 
            DirectoryInUseException,
            Exception 
    {
        String request = JsonParser.getJsonString("uuid",UUID,"path",path);
        HashMap<String,String> responseMap;
        try {
            responseMap = sendPostRequest("/delete_directory",request);
        } catch (InterruptedException e) { throw new IOException();}
        String code = responseMap.get("code");
        switch (code) {
            case "200": return true;
            case "500": throw new Exception();
            case "407": throw new PathNotManagedException("Path not managed");
            case "408": throw new DirectoryInUseException("Provided directory has open transactions");
            default: throw new Exception();
        }
    }

    @Override
    protected void finalize() throws Throwable {
        // More of a small band-aid on a flesh wound, but as long as the JVM isn't closed before
        // the gc can get here it should be fine.
        // If not, the transaction handler will have some abandoned uuids floating around until
        // restart. "Should be fine"
        deregister();
    }

// ==================================================================
// API Interaction
// ==================================================================
    /** Method: sendGetRequest
     * @param target : Target resource sub-address. Resolves to {ADDRESS}{target}.
     * @return responseMap : content of response json as HashMap.
     */
    private HashMap<String,String> sendGetRequest(String target) throws IOException,InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(ADDRESS+target))
            .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        String responseBody = response.body();
        HashMap<String,String> responseMap = JsonParser.parseJsonString(responseBody);
        return responseMap;
    }
    /** Method: sendPostRequest
     * @param target : Target resource sub-address. Resolves to {ADDRESS}{target}.
     * @param jsonPayloadString : String containing the request payload as json.
     * @return responseMap : content of response json as HashMap.
     */
    private HashMap<String,String> sendPostRequest(String target, String jsonPayloadString) throws IOException,InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(ADDRESS+target))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayloadString))
            .build();
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        String responseBody = response.body();
        HashMap<String,String> responseMap = JsonParser.parseJsonString(responseBody);
        return responseMap;
    }
}