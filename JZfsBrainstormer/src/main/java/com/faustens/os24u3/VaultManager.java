package com.faustens.os24u3;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import com.faustens.os24u3.TransactionHandler;
import com.faustens.os24u3.exceptions.*;

public class VaultManager {
    String path;
    HashMap<String,String> notes;
    TransactionHandler handler;
    static TransactionHandler staticHandler = TransactionHandler.newTransactionHandler();
    File currentNoteFile = null;
    Note currentNote = null;

    protected VaultManager(String path) {
        this.path = path;
        notes = new HashMap<>();
        handler = TransactionHandler.newTransactionHandler();
    }

    // ========================================================================
    // Intsance-specific Methods
    // ========================================================================
    protected ArrayList<String> getNoteNames() {
        ArrayList<String> noteNames = new ArrayList<>();
        File folder = new File(path);

        if (!folder.exists() || !folder.isDirectory()) return null;
        File[] files = folder.listFiles((dir, name) -> name.toLowerCase().endsWith(".xml"));
        if (files == null) return null;
        for (File file : files) {
            String fileName = file.getName().replaceFirst("\\.xml", "");
            noteNames.add(fileName);
        }

        return noteNames;
    }

    protected void printNotes() {
        ArrayList<String> noteNames = getNoteNames();
        if (noteNames == null) return;
        
        StringBuilder builder = new StringBuilder();
        for (int i=0; i<noteNames.size(); i++) {
            builder.append(String.format("%3d. %s", i, noteNames.get(i)));
        }
        System.out.println(builder.toString());
    }

    protected boolean openNote(String noteName) throws Exception{
        if (currentNote != null)  closeOpenNote();
        if (!getNoteNames().contains(noteName)) return false;
        if (!noteName.contains(".xml")) noteName = noteName + ".xml";
        try {
        currentNoteFile = handler.openFile(this.path + "/" + noteName);
        } catch (Exception e) {}
        currentNote = Note.xmlToNote(currentNoteFile);
        return true;
    }

    protected void printOpenNote() {
        System.out.println(this.currentNote.toString());
    }

    protected void closeOpenNote() throws Exception {
        handler.cancelFile(this.currentNoteFile);
        this.currentNote = null;
        this.currentNoteFile = null;
    }

    protected void commentOpenNote(String comment) throws Exception{
        currentNote.addComment(comment);
        currentNote.saveToXML(currentNoteFile);
        handler.commitFile(currentNoteFile);
        this.currentNote = null;
        this.currentNoteFile = null;
    }

    protected void addNote(String title, String content) throws Exception {
        if (getNoteNames().contains(title)) return;
        String filename = title + ".xml";
        String filepath = path + "/" + filename;
        handler.createFile(filepath);
        File file = handler.openFile(filepath);
        Note note = new Note(title, content);
        note.saveToXML(file);
        handler.commitFile(file); 
    }

    protected void close() throws Exception {
        if (currentNoteFile != null) handler.cancelFile(currentNoteFile);
        handler.close();
        staticHandler.close();
    }

    // ========================================================================
    // Static Methods
    // ========================================================================
    protected static boolean makeVault(String path) {
        if (isVault(path)) {
            System.out.println("Provided path already is a vault");
            return false;
        }
        try {
            System.out.println("Before Path creation.");
            staticHandler.createDirectory(path);
        } catch (PathExistsException pee) {
            // Do Nothing
        } catch (PathNotManagedException pnme) {
            System.out.println("Provided Path is not managed by ZFS");
            return false;
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            staticHandler.createFile(path + "/vaultfile");
            return true;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }

    protected static VaultManager openVault(String path) {
        VaultManager manager = new VaultManager(path);
        return manager;
    }

    protected static boolean isVault(String path) {
        File folder = new File(path);

        if (!folder.exists() || !folder.isDirectory()) return false;
        File[] files = folder.listFiles();
        if (files == null) return false;
        for (File file : files) {
            if (file.getName().equals("vaultfile")) return true;
        }
        return false;
    }


}
