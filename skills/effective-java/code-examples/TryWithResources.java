package effectivejava.item9;

import java.io.*;

/**
 * Item 9: Always use try-with-resources in preference to try-finally
 * 
 * The try-with-resources statement is shorter and clearer,
 * and the exceptions that it generates are more useful.
 */
public class TryWithResources {

    // BAD - try-finally is ugly when using multiple resources
    static String firstLineOfFileBad(String path) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(path));
        try {
            return br.readLine();
        } finally {
            br.close();
        }
    }

    // GOOD - try-with-resources is clean and correct
    static String firstLineOfFileGood(String path) throws IOException {
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            return br.readLine();
        }
    }

    // Multiple resources
    static void copy(String src, String dst) throws IOException {
        try (InputStream in = new FileInputStream(src);
             OutputStream out = new FileOutputStream(dst)) {
            byte[] buf = new byte[1024];
            int n;
            while ((n = in.read(buf)) >= 0)
                out.write(buf, 0, n);
        }
    }

    public static void main(String[] args) {
        // Create a test file
        try {
            File temp = File.createTempFile("test", ".txt");
            try (PrintWriter pw = new PrintWriter(temp)) {
                pw.println("Hello, Effective Java!");
            }

            String line = firstLineOfFileGood(temp.getAbsolutePath());
            System.out.println("First line: " + line);

            temp.delete();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
