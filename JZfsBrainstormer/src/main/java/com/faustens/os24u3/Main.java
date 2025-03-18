package com.faustens.os24u3;

import java.nio.file.InvalidPathException;
import java.nio.file.Paths;
import java.util.Scanner;

/**
 * Hello world!
 *
 */
public class Main
{
    public static void main(String[] args )
    {
        if (args.length != 2) {
            System.out.println("Usage: 'java -jar JZfsBrainstormer.jar <make|open|check> <path>'");
            return;
        }

        String interactionType = args[0];
        String path = args[1];

        switch (interactionType) {
            case "make":
                VaultManager.makeVault(path);
                return;
            case "open":
                if (!isValidPath(path)) {
                    System.out.println(String.format("'%s' is not a valid path", path));
                    return;
                }
                if (VaultManager.isVault(path)) {
                    openVaultMainLoop(new VaultManager(path));
                } else {
                    System.out.println(String.format("'%s' is not a JZfsBrainstormer Vault", path));
                }
                return;
            case "check": 
                if (VaultManager.isVault(path)) {
                    System.out.println(String.format("'%s' is a JZfsBrainstormer Vault", path));
                } else {
                    System.out.println(String.format("'%s' is not a JZfsBrainstormer Vault", path));
                }
                return;
            default:
                System.out.println("Invalid interaction type.");
                System.out.println("Usage: 'java -jar JZfsBrainstormer.jar <make|open|chek> <path>'");
                return;
        }
    }

    private static void openVaultMainLoop(VaultManager manager) {
        boolean closed = false;
        Scanner scanner = new Scanner(System.in);
        while (!closed) {
            System.out.println("Welcome to the Idea Vault. What do you want to do:\n 1. list\n 2. open <note_name>\n 3. create\n 4. close");
            String input = scanner.nextLine();
            String[] inputArray = input.split(" (?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)");
            try {
                switch(inputArray[0]) {
                    case "list":
                        manager.printNotes();
                        break;
                    case "open":
                        boolean success = manager.openNote(inputArray[1].replace("\"",""));
                        if (!success) {
                            System.out.println("The provided Name does not correspond to a note.");
                            break;
                        }
                        manager.printOpenNote();
                        System.out.println("What do you wish to do\n 1. comment\n 2. close"); // The illusion of choice
                        String input2 = scanner.nextLine();
                        switch (input2) {
                            case "comment":
                                System.out.println("Please enter your comment:\n");
                                String comment = scanner.nextLine();
                                manager.commentOpenNote(comment);
                                break;
                            default:
                                manager.closeOpenNote();
                                break;
                        }
                        break;
                    case "create":
                        System.out.println("Enter note title:");
                        String title = scanner.nextLine();
                        System.out.println("Enter note content:");
                        String content = scanner.nextLine();
                        manager.addNote(title,content);
                        break;
                    case "close":
                        manager.close();
                        closed = true;
                        break;
                    default:
                        break;
                }
            } catch (Exception e) {
                System.out.println("Something went wrong");
            }
        }
        try {
            manager.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        
    }

    private static boolean isValidPath(String path) {
        try {
            Paths.get(path);
            return true;
        } catch (InvalidPathException e) {
            return false;
        }
    }
}
