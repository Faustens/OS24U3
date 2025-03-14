package com.fausens.os24u3;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.HashMap;

import com.faustens.os24u3.JsonParser;
import com.faustens.os24u3.TransactionHandler;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

/**
 * Unit test for simple App.
 */
public class AppTest 
    extends TestCase
{
    /**
     * Create the test case
     *
     * @param testName name of the test case
     */
    public AppTest( String testName )
    {
        super( testName );
    }

    /**
     * @return the suite of tests being tested
     */
    public static Test suite()
    {
        return new TestSuite( AppTest.class );
    }

    public void testJsonStringToMap() {
        String json = "{\"key1\":\"value1\",\"key2\":\"value2\"}";
        HashMap<String,String> jsonMap = new HashMap<>();
        jsonMap.put("key1","value1");
        jsonMap.put("key2","value2");
        HashMap<String,String> newMap = JsonParser.parseJsonString(json);
        boolean equal = newMap.equals(jsonMap);
        assertTrue(equal);
    }

    public void testJsonMapToString() {
        String json = "{\"key1\":\"value1\",\"key2\":\"value2\"}";
        HashMap<String,String> jsonMap = new HashMap<>();
        jsonMap.put("key1","value1");
        jsonMap.put("key2","value2");
        String newString = JsonParser.mapToJsonString(jsonMap);
        boolean equal = newString.equals(json);
        assertTrue(equal);
    }

    /*
    public void testFileCommit() {
        TransactionHandler handler = TransactionHandler.newTransactionHandler();
        System.out.println(handler);
        boolean noException = true;
        
        try {
			File file = handler.openFile("/mypool/testdir/test.txt");
			BufferedWriter writer;
			writer = new BufferedWriter(new FileWriter(file));
			writer.write("This is another test.",0,21);
			writer.flush();
			writer.close();
			handler.commitFile(file);
		} catch (Exception e) {
			e.printStackTrace();
            noException = false;
			return;
		} finally {
			handler.close();
            assertTrue(noException);
		}
    }*/
    /*
    public void testCommitCancel() {
        TransactionHandler handler = TransactionHandler.newTransactionHandler();
        System.out.println(handler);
        boolean noException = true;
        
        try {
			File file = handler.openFile("/mypool/testdir/test.txt");
			BufferedWriter writer;
			writer = new BufferedWriter(new FileWriter(file));
			writer.write("This is a cancel test.\nJAHAHAAHA",0,22);
			writer.flush();
			writer.close();
			handler.cancelFile(file);
		} catch (Exception e) {
			e.printStackTrace();
            noException = false;
			return;
		} finally {
			handler.close();
            assertTrue(noException);
		}
    }
    */

    public void allroundTest() {
        TransactionHandler handler = TransactionHandler.newTransactionHandler();
        System.out.println(handler);
        boolean noException = true;
        
        try {
            String path = "/mypool/foo/";
            String filePath = path+"/bar.txt";
            handler.createDirectory(path);
            handler.createFile(filePath);
			File file = handler.openFile(filePath);
			BufferedWriter writer;
			writer = new BufferedWriter(new FileWriter(file));
			writer.write("This is a cancel test.\nJAHAHAAHA",0,22);
			writer.flush();
			writer.close();
			handler.cancelFile(file);
            handler.deleteFile(filePath);
            handler.deleteDirectory(path);
		} catch (Exception e) {
			e.printStackTrace();
            noException = false;
			return;
		} finally {
			handler.close();
            assertTrue(noException);
		}
    }
}
