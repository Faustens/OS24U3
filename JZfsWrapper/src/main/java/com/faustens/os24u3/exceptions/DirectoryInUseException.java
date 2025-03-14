package com.faustens.os24u3.exceptions;

public class DirectoryInUseException extends JZfsException {
    public DirectoryInUseException(String message) {
        super(message);
    }
}
