package com.integration.util;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.ConsoleHandler;
import java.util.logging.Formatter;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;

public class LogUtil {

    private static boolean initialized = false;

    public static void configureRootLogger() {
        if (initialized) return;
        initialized = true;

        Logger rootLogger = Logger.getLogger("");
        rootLogger.setLevel(Level.INFO);

        for (java.util.logging.Handler h : rootLogger.getHandlers()) {
            rootLogger.removeHandler(h);
        }

        ConsoleHandler handler = new ConsoleHandler();
        handler.setLevel(Level.INFO);
        handler.setFormatter(new Formatter() {
            private final SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
            @Override
            public String format(LogRecord record) {
                StringBuilder sb = new StringBuilder();
                sb.append(sdf.format(new Date(record.getMillis())));
                sb.append(" [").append(record.getLevel().getName()).append("] ");
                sb.append("[").append(record.getLoggerName()).append("] ");
                sb.append(formatMessage(record));
                if (record.getThrown() != null) {
                    sb.append("\n");
                    for (StackTraceElement el : record.getThrown().getStackTrace()) {
                        sb.append("    at ").append(el.toString()).append("\n");
                    }
                }
                sb.append("\n");
                return sb.toString();
            }
        });
        rootLogger.addHandler(handler);
    }

    public static Logger getLogger(Class<?> clazz) {
        return Logger.getLogger(clazz.getName());
    }
}
