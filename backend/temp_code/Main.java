import javax.swing.*;
import java.awt.*;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Main {

    private static JComboBox<String> inputLanguageChoiceMenu;
    private static JComboBox<String> translateLanguageChoiceMenu;
    private static JTextField textVar;
    private static JTextField outputVar;
    private static final Map<String, String> languageCodes = new HashMap<>();

    static {
        languageCodes.put("Hindi", "hi");
        languageCodes.put("English", "en");
        languageCodes.put("French", "fr");
        languageCodes.put("German", "de");
        languageCodes.put("Spanish", "es");
        languageCodes.put("Tamil", "ta");
    }

    private static class Translator {
        public static String translate(String fromLang, String toLang, String text) throws Exception {
            if (text == null || text.isBlank()) {
                return "";
            }
            String encodedText = URLEncoder.encode(text, StandardCharsets.UTF_8);
            String langPair = fromLang + "|" + toLang;
            String urlStr = "https://api.mymemory.translated.net/get?q=" + encodedText + "&langpair=" + langPair;

            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(urlStr))
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            return parseTranslatedText(response.body());
        }

        private static String parseTranslatedText(String jsonResponse) {
            Pattern pattern = Pattern.compile("\"translatedText\":\"(.*?)\"");
            Matcher matcher = pattern.matcher(jsonResponse);
            if (matcher.find()) {
                return matcher.group(1);
            }
            return "Translation not found";
        }
    }

    private static void Translate() {
        String fromLangName = (String) inputLanguageChoiceMenu.getSelectedItem();
        String toLangName = (String) translateLanguageChoiceMenu.getSelectedItem();
        String textToTranslate = textVar.getText();

        if (fromLangName == null || toLangName == null || textToTranslate.isBlank()) {
            outputVar.setText("");
            return;
        }

        String fromLangCode = languageCodes.get(fromLangName);
        String toLangCode = languageCodes.get(toLangName);

        outputVar.setText("Translating...");

        // Network operations should not be on the Event Dispatch Thread
        new Thread(() -> {
            try {
                String translation = Translator.translate(fromLangCode, toLangCode, textToTranslate);
                SwingUtilities.invokeLater(() -> outputVar.setText(translation));
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> outputVar.setText("Error: Could not translate"));
                e.printStackTrace();
            }
        }).start();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame screen = new JFrame("Language Translator with GUI by- TechVidvan");
            screen.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            screen.setLayout(new GridBagLayout());
            screen.setResizable(false);

            String[] languageChoices = {"Hindi", "English", "French", "German", "Spanish", "Tamil"};
            GridBagConstraints gbc = new GridBagConstraints();
            gbc.insets = new Insets(5, 5, 5, 5);
            gbc.fill = GridBagConstraints.HORIZONTAL;

            // Row 0
            gbc.gridx = 1;
            gbc.gridy = 0;
            screen.add(new JLabel("Choose a Language"), gbc);

            gbc.gridx = 2;
            screen.add(new JLabel("Translated Language"), gbc);

            // Row 1
            inputLanguageChoiceMenu = new JComboBox<>(languageChoices);
            inputLanguageChoiceMenu.setSelectedItem("English");
            gbc.gridx = 1;
            gbc.gridy = 1;
            screen.add(inputLanguageChoiceMenu, gbc);

            translateLanguageChoiceMenu = new JComboBox<>(languageChoices);
            translateLanguageChoiceMenu.setSelectedItem("Tamil");
            gbc.gridx = 2;
            screen.add(translateLanguageChoiceMenu, gbc);

            // Row 2
            gbc.fill = GridBagConstraints.NONE;
            gbc.anchor = GridBagConstraints.EAST;
            gbc.gridx = 0;
            gbc.gridy = 2;
            screen.add(new JLabel("Enter Text"), gbc);

            gbc.anchor = GridBagConstraints.WEST;
            gbc.fill = GridBagConstraints.HORIZONTAL;
            textVar = new JTextField(20);
            gbc.gridx = 1;
            screen.add(textVar, gbc);
            
            gbc.fill = GridBagConstraints.NONE;
            gbc.anchor = GridBagConstraints.EAST;
            gbc.gridx = 2;
            screen.add(new JLabel("Output Text"), gbc);

            gbc.anchor = GridBagConstraints.WEST;
            gbc.fill = GridBagConstraints.HORIZONTAL;
            outputVar = new JTextField(20);
            outputVar.setEditable(false);
            gbc.gridx = 3;
            screen.add(outputVar, gbc);

            // Row 3
            JButton b = new JButton("Translate");
            b.addActionListener(e -> Translate());
            gbc.gridx = 1;
            gbc.gridy = 3;
            gbc.gridwidth = 3;
            screen.add(b, gbc);

            screen.pack();
            screen.setLocationRelativeTo(null);
            screen.setVisible(true);
        });
    }
}