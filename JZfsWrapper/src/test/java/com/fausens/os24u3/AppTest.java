package com.fausens.os24u3;

import java.util.HashMap;

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
}
