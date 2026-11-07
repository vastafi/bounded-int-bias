// Integers 0..n-1 from Java, two ways.
//   nextint   : new Random(seed).nextInt(n)              (rejection: unbiased, 31-bit source)
//   intdouble : (long) (rnd.nextDouble() * n)            (mult, w = 53)
// Run without compiling (Java 11+): java src/languages/java/SampleJava.java <n> <N> <seed> <outdir>
import java.io.*;
import java.nio.file.*;
import java.util.Random;

public class SampleJava {
    public static void main(String[] a) throws IOException {
        int n = Integer.parseInt(a[0]);
        int N = Integer.parseInt(a[1]);
        long seed = Long.parseLong(a[2]);
        Path out = Paths.get(a[3]);
        Files.createDirectories(out);
        String tag = "n" + n + "_N" + N + "_seed" + seed;

        Random r = new Random(seed);
        try (PrintWriter w = new PrintWriter(new BufferedWriter(new FileWriter(out.resolve("java_nextint_" + tag + ".txt").toFile())))) {
            for (int i = 0; i < N; i++) w.println(r.nextInt(n));
        }
        r = new Random(seed);
        try (PrintWriter w = new PrintWriter(new BufferedWriter(new FileWriter(out.resolve("java_intdouble_" + tag + ".txt").toFile())))) {
            for (int i = 0; i < N; i++) w.println((long) (r.nextDouble() * n));
        }
        Files.write(out.resolve("version.txt"), (System.getProperty("java.version") + " " + System.getProperty("java.vendor") + "\n").getBytes());
    }
}
