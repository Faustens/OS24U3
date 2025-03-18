package com.faustens.os24u3;

import java.io.File;
import java.util.ArrayList;
import org.w3c.dom.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

public class Note {
    String title, content;
    ArrayList<String> comments;

    public Note(String title, String content, ArrayList<String> comments) {
        this.title = title;
        this.content = content;
        this.comments = comments;
    }

    public Note(String title, String content) {
        this.title = title;
        this.content = content;
        this.comments = new ArrayList<>();
    }

    public void addComment(String comment) {
        this.comments.add(comment);
    }

    public static Note xmlToNote(File xmlFile) {
        try {
            Document doc = DocumentBuilderFactory.newInstance()
                                .newDocumentBuilder()
                                .parse(xmlFile);
            doc.getDocumentElement().normalize();
            String title = doc.getElementsByTagName("Title")
                                .item(0)
                                .getTextContent();
            String content = doc.getElementsByTagName("Title")
                                .item(0)
                                .getTextContent();
            NodeList commentNodes = doc.getElementsByTagName("Comment");
            ArrayList<String> comments = new ArrayList<>();
            for (int i=0; i<commentNodes.getLength(); i++) {
                comments.add(commentNodes.item(i).getTextContent());
            }
            return new Note(title, content, comments);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public void saveToXML(File targetFile) {
        try {
            Document doc = DocumentBuilderFactory.newInstance()
                                    .newDocumentBuilder()
                                    .newDocument();
            Element rootNode = doc.createElement("Note");
            doc.appendChild(rootNode);

            Element titleNode = doc.createElement("Title");
            titleNode.appendChild(doc.createTextNode(this.title));
            rootNode.appendChild(titleNode);

            Element contentNode = doc.createElement("Content");
            contentNode.appendChild(doc.createTextNode(this.content));
            rootNode.appendChild(contentNode);

            for (String comment : this.comments) {
                Element commentNode = doc.createElement("Comment");
                commentNode.appendChild(doc.createTextNode(comment));
                rootNode.appendChild(commentNode);
            }

            Transformer transformer = TransformerFactory.newInstance().newTransformer();
            transformer.setOutputProperty(OutputKeys.INDENT, "yes");
            DOMSource source = new DOMSource(doc);
            StreamResult result = new StreamResult(targetFile);
            transformer.transform(source, result);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public String toString() {
        StringBuilder builder = new StringBuilder();
        builder.append("[ Title    ]============================\n");
        builder.append(String.format("%s\n", title));
        builder.append("[ Content  ]============================\n");
        builder.append(String.format("%s\n", content));
        builder.append("[ Comments ]============================\n");
        for (String comment : comments) {
            builder.append("- %s\n");
        }
        builder.append("========================================\n");
        return builder.toString();
    }
}
