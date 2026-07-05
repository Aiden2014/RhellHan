using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace RhellHan;

public static class TranslationManager
{
    // key: TranslationOriginalText list string, value: TranslationTranslatedText list
    public static Dictionary<string, List<string>> DialogueTranslations = [];
    public static Dictionary<string, List<string>> SummaryTranslations = [];
    public static Dictionary<string, string> TextTranslations = [];
    public static Dictionary<string, string> SettingTextTranslations = [];
    public static List<string> HintTranslations = [];
    public static List<string> DemoHintTranslations = [];
    public static List<string> FinishedRandomHintTranslations = [];
    public static Dictionary<string, string> MapLocationHightlightTranslations = [];
    public static List<string> RuneNameTranslations = [];
    public static List<string> RuneDescriptionTranslations = [];
    public static List<string> ItemNameTranslations = [];
    public static List<string> ItemDescriptionTranslations = [];
    public static Dictionary<string, List<string>> DialogueOptionTranslations = [];
    public static Dictionary<string, string> DialogueOptionTextTranslations = [];
    public static Dictionary<string, string> TabDescriptionTranslations = [];
    public static Dictionary<string, string> RoomHintTranslations = [];
    public static Dictionary<string, string> StoryPointTranslations = [];
    public static List<string> WorldNameTranslations = [];
    public static Dictionary<string, string> TextMeshProTranslations = [];
    public static Dictionary<string, string> CheatTitleTranslations = [];
    public static Dictionary<string, string> CheatDescriptionTranslations = [];
    public static Dictionary<string, string> ChallengeMenuTranslations = [];
    public static Dictionary<string, string> SelectableSpellNameTranslations = [];
    public static Dictionary<string, string> SelectableSpellDescriptionTranslations = [];
    public static Dictionary<string, string> EndpointTranslations = [];
    public static Dictionary<string, string> DirectionKeyTranslations = [];
    public static Dictionary<string, string> TextMeshProUGUITranslations = [];
    public static Dictionary<string, string> RanzomierMenuTranslations = [];

    public static void Init()
    {
        InitDialogue();
        InitSummary();
        InitText();
        InitSettingText();
        InitHint();
        InitMapLocationHighlight();
        InitPlayerInventory();
        InitDialogueOption();
        InitTabDescription();
        InitRoomHint();
        InitStoryPoint();
        InitWorldName();
        InitTextMeshPro();
        InitCheat();
        InitChallengeMenu();
        InitSelectableSpells();
        InitEndpoint();
        InitDirectionKey();
        InitTextMeshProUGUI();
        InitRandomized();
    }

    private static void InitDirectionKey()
    {
        // InputSystem 原始路径名
        DirectionKeyTranslations["Up Arrow"] = "↑";
        DirectionKeyTranslations["Down Arrow"] = "↓";
        DirectionKeyTranslations["Left Arrow"] = "←";
        DirectionKeyTranslations["Right Arrow"] = "→";
        // 人类可读格式（InputSystem 可能在某些地方生成）
        DirectionKeyTranslations["Up"] = "↑";
        DirectionKeyTranslations["Down"] = "↓";
        DirectionKeyTranslations["Left"] = "←";
        DirectionKeyTranslations["Right"] = "→";

        DirectionKeyTranslations["Control"] = "Ctrl";
    }

    private static void InitDialogue()
    {
        var dialogueTranslationsRows = ResourceLoader.GetTranslationRows(
            "dialogue_filtered.csv",
            4
        );
        // key: TranslationKey[0] + "|||" + TranslationKey[1]. value: [TranslationOriginalText list, TranslationTranslatedText list]
        var dialogueBundleMap = new Dictionary<string, List<List<string>>>();
        foreach (var dialogueTranslationRow in dialogueTranslationsRows)
        {
            var dialogueKey =
                dialogueTranslationRow.TranslationKey[0]
                + "|||"
                + dialogueTranslationRow.TranslationKey[1];
            if (!dialogueBundleMap.ContainsKey(dialogueKey))
            {
                dialogueBundleMap[dialogueKey] = new List<List<string>>();
            }

            dialogueBundleMap[dialogueKey]
                .Add([
                    dialogueTranslationRow.TranslationOriginalText,
                    dialogueTranslationRow.TranslationTranslatedText,
                ]);
        }
        foreach (var dialogueBundle in dialogueBundleMap)
        {
            var dialogueKey = string.Join("|||", dialogueBundle.Value.Select(v => v[0]));
            var dialogueValue = new List<string>();

            foreach (var translationList in dialogueBundle.Value)
            {
                dialogueValue.Add(translationList[1]);
            }
            DialogueTranslations[dialogueKey] = dialogueValue;
        }
    }

    private static void InitSummary()
    {
        var summaryTranslationsRows = ResourceLoader.GetTranslationRows("summary.csv", 4);
        // key: TranslationKey[0]. value: [TranslationOriginalText list, TranslationTranslatedText list]
        var summaryBundleMap = new Dictionary<string, List<List<string>>>();
        foreach (var summaryTranslationRow in summaryTranslationsRows)
        {
            var summaryKey = summaryTranslationRow.TranslationKey[0];
            if (!summaryBundleMap.ContainsKey(summaryKey))
            {
                summaryBundleMap[summaryKey] = new List<List<string>>();
            }

            summaryBundleMap[summaryKey]
                .Add([
                    summaryTranslationRow.TranslationOriginalText,
                    summaryTranslationRow.TranslationTranslatedText,
                ]);
        }
        foreach (var summaryBundle in summaryBundleMap)
        {
            var summaryKey = string.Join("|||", summaryBundle.Value.Select(v => v[0]));
            var summaryValue = new List<string>();
            foreach (var translationList in summaryBundle.Value)
            {
                summaryValue.Add(translationList[1]);
            }
            SummaryTranslations[summaryKey] = summaryValue;
        }
    }

    public static string NormalizeNewlines(string s)
    {
        return s.Replace("\\n", "\n").Replace("\r\n", "\n").Replace("\r", "\n").Trim();
    }

    private static void InitText()
    {
        var textTranslationRows = ResourceLoader.GetTranslationRows("text.csv", 1);
        foreach (var textTranslationRow in textTranslationRows)
        {
            if (
                textTranslationRow.TranslationOriginalText.Equals(
                    textTranslationRow.TranslationTranslatedText
                )
            )
            {
                continue;
            }
            var textKey = NormalizeNewlines(textTranslationRow.TranslationOriginalText);
            var textValue = NormalizeNewlines(textTranslationRow.TranslationTranslatedText);
            TextTranslations[textKey] = textValue;
        }
        // Add hardcoded translations for text that is not in the CSV file
        TextTranslations["quit challenge"] = "退出挑战";
    }

    private static void InitSettingText()
    {
        SettingTextTranslations["on"] = "开";
        SettingTextTranslations["off"] = "关";
        SettingTextTranslations["type1"] = "类型1";
        SettingTextTranslations["type2"] = "类型2";
        SettingTextTranslations["mild"] = "弱";
        SettingTextTranslations["strong"] = "强";
        SettingTextTranslations["normal"] = "正常";
        SettingTextTranslations["light"] = "明显";
        SettingTextTranslations["disabled"] = "禁用";
        SettingTextTranslations["enabled"] = "启用";
        SettingTextTranslations["Deuteranopia"] = "绿色盲";
        SettingTextTranslations["Protanopia"] = "红色盲";
        SettingTextTranslations["Tritanopia"] = "蓝色盲";
        SettingTextTranslations["Monochromatism"] = "单色盲";
        SettingTextTranslations["fast"] = "快速";
    }

    private static void InitHint()
    {
        var hintTranslationRows = ResourceLoader
            .GetTranslationRows("hint.csv", 3)
            .OrderBy(x =>
            {
                if (int.TryParse(x.TranslationKey[1], out int result))
                {
                    return result;
                }
                Plugin.Logger.LogWarning(
                    $"Failed to parse hint key: {string.Join("|||", x.TranslationKey)}"
                );
                return int.MaxValue;
            })
            .ToList();
        foreach (var hintTranslationRow in hintTranslationRows)
        {
            var hintValue = hintTranslationRow.TranslationTranslatedText;
            if (hintTranslationRow.TranslationKey[0].Equals("hints"))
            {
                HintTranslations.Add(hintValue);
            }
            else if (hintTranslationRow.TranslationKey[0].Equals("demohints"))
            {
                DemoHintTranslations.Add(hintValue);
            }
            else if (hintTranslationRow.TranslationKey[0].Equals("finishedRandomHints"))
            {
                FinishedRandomHintTranslations.Add(hintValue);
            }
        }
    }

    private static void InitMapLocationHighlight()
    {
        var mapLocationHighlightRows = ResourceLoader.GetTranslationRows(
            "map_location_highlight.csv",
            1
        );
        foreach (var row in mapLocationHighlightRows)
        {
            var key = row.TranslationKey[0];
            var value = InsertManualBreaks(row.TranslationTranslatedText, 54);
            MapLocationHightlightTranslations[key] = value;
        }
    }

    private static void InitPlayerInventory()
    {
        LoadAndSortName("rune_name.csv", RuneNameTranslations);
        LoadAndSortName("item_name.csv", ItemNameTranslations);
        LoadAndSortDescription("rune_description.csv", RuneDescriptionTranslations);
        LoadAndSortDescription("item_description.csv", ItemDescriptionTranslations);
    }

    private static void LoadAndSortDescription(string fileName, List<string> translationList)
    {
        var descriptionRows = ResourceLoader
            .GetTranslationRows(fileName, 3)
            .OrderBy(x =>
            {
                if (int.TryParse(x.TranslationKey[0], out int result))
                {
                    return result;
                }
                Plugin.Logger.LogWarning(
                    $"Failed to parse {fileName} key: {string.Join("|||", x.TranslationKey)}"
                );
                return int.MaxValue;
            })
            .ToList();
        foreach (var row in descriptionRows)
        {
            var value = InsertManualBreaks(row.TranslationTranslatedText, 50);
            translationList.Add(value);
        }
    }

    private static void LoadAndSortName(string fileName, List<string> translationList)
    {
        var nameRows = ResourceLoader
            .GetTranslationRows(fileName, 2)
            .OrderBy(x =>
            {
                if (int.TryParse(x.TranslationKey[0], out int result))
                {
                    return result;
                }
                Plugin.Logger.LogWarning(
                    $"Failed to parse {fileName} key: {string.Join("|||", x.TranslationKey)}"
                );
                return int.MaxValue;
            })
            .ToList();
        foreach (var row in nameRows)
        {
            var value = row.TranslationTranslatedText;
            translationList.Add(value);
        }
    }

    private static void InitDialogueOption()
    {
        var dialogueOptionTranslationRows = ResourceLoader.GetTranslationRows(
            "dialogue_option.csv",
            4
        );
        // key: TranslationKey[0] + "|||" + TranslationKey[1]. value: [TranslationOriginalText list, TranslationTranslatedText list]
        var dialogueOptionBundleMap = new Dictionary<string, List<List<string>>>();
        foreach (var dialogueOptionTranslationRow in dialogueOptionTranslationRows)
        {
            var dialogueOptionKey =
                dialogueOptionTranslationRow.TranslationKey[0]
                + "|||"
                + dialogueOptionTranslationRow.TranslationKey[1];
            if (!dialogueOptionBundleMap.ContainsKey(dialogueOptionKey))
            {
                dialogueOptionBundleMap[dialogueOptionKey] = new List<List<string>>();
            }

            dialogueOptionBundleMap[dialogueOptionKey]
                .Add([
                    dialogueOptionTranslationRow.TranslationOriginalText,
                    dialogueOptionTranslationRow.TranslationTranslatedText,
                ]);
            DialogueOptionTextTranslations[dialogueOptionTranslationRow.TranslationOriginalText] =
                dialogueOptionTranslationRow.TranslationTranslatedText;
        }
        foreach (var dialogueOptionBundle in dialogueOptionBundleMap)
        {
            var dialogueOptionKey = string.Join(
                "|||",
                dialogueOptionBundle.Value.Select(v => v[0])
            );
            var dialogueOptionValue = new List<string>();

            foreach (var translationList in dialogueOptionBundle.Value)
            {
                dialogueOptionValue.Add(translationList[1]);
            }
            DialogueOptionTranslations[dialogueOptionKey] = dialogueOptionValue;
        }
    }

    private static void InitTabDescription()
    {
        var rows = ResourceLoader.GetTranslationRows("item_tab_description.csv", 1);
        foreach (var row in rows)
        {
            TabDescriptionTranslations[row.TranslationOriginalText] = InsertManualBreaks(
                row.TranslationTranslatedText,
                50
            );
        }
    }

    private static void InitRoomHint()
    {
        var rows = ResourceLoader.GetTranslationRows("room_hint.csv", 1);
        foreach (var row in rows)
        {
            RoomHintTranslations[row.TranslationOriginalText] = row.TranslationTranslatedText;
        }
    }

    private static void InitStoryPoint()
    {
        var rows = ResourceLoader.GetTranslationRows("storypoint.csv", 3);
        var total = 0;
        var hasChinese = 0;
        foreach (var row in rows)
        {
            total++;
            if (row.TranslationOriginalText != row.TranslationTranslatedText)
                hasChinese++;
            StoryPointTranslations[row.TranslationOriginalText.Trim()] =
                row.TranslationTranslatedText;
        }
        Plugin.Logger.LogInfo($"InitStoryPoint: {total} entries, {hasChinese} translated");
    }

    private static void InitWorldName()
    {
        var rows = ResourceLoader
            .GetTranslationRows("world_name.csv", 2)
            .OrderBy(x =>
            {
                if (int.TryParse(x.TranslationKey[0], out int result))
                    return result;
                return int.MaxValue;
            })
            .ToList();
        foreach (var row in rows)
            WorldNameTranslations.Add(row.TranslationTranslatedText);
        Plugin.Logger.LogInfo($"InitWorldName: {WorldNameTranslations.Count} entries");
    }

    private static void InitTextMeshPro()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("text_mesh_pro.csv", 1))
        {
            var key = NormalizeNewlines(row.TranslationOriginalText);
            var value = NormalizeNewlines(row.TranslationTranslatedText);
            TextMeshProTranslations[key] = value;
        }
    }

    private static void InitCheat()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("cheat_title.csv", 1))
        {
            CheatTitleTranslations[row.TranslationOriginalText] = row.TranslationTranslatedText;
        }
        foreach (var row in ResourceLoader.GetTranslationRows("cheat_description.csv", 1))
        {
            CheatDescriptionTranslations[row.TranslationOriginalText] = InsertManualBreaks(
                row.TranslationTranslatedText,
                28
            );
        }
    }

    private static void InitChallengeMenu()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("challenge_menu.csv", 1))
        {
            ChallengeMenuTranslations[NormalizeNewlines(row.TranslationOriginalText)] =
                NormalizeNewlines(row.TranslationTranslatedText);
        }
    }

    private static void InitSelectableSpells()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("selectable_spell_name.csv", 1))
        {
            SelectableSpellNameTranslations[row.TranslationOriginalText] =
                row.TranslationTranslatedText;
        }
        foreach (
            var row in ResourceLoader.GetTranslationRows("selectable_spell_description.csv", 2)
        )
        {
            SelectableSpellDescriptionTranslations[row.TranslationOriginalText] =
                InsertManualBreaks(row.TranslationTranslatedText, 10);
        }
    }

    private static void InitEndpoint()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("endpoint.csv", 2))
        {
            EndpointTranslations[row.TranslationOriginalText] = row.TranslationTranslatedText;
        }
    }

    private static void InitTextMeshProUGUI()
    {
        foreach (var row in ResourceLoader.GetTranslationRows("text_mesh_pro_ugui.csv", 1))
        {
            var key = NormalizeNewlines(row.TranslationOriginalText);
            var value = NormalizeNewlines(row.TranslationTranslatedText);
            TextMeshProUGUITranslations[key] = value;
        }
    }

    private static void InitRandomized()
    {
        // difficulty
        RanzomierMenuTranslations["0 off"] = "0 关";
        RanzomierMenuTranslations["1 very easy"] = "1 非常简单";
        RanzomierMenuTranslations["2 very easy"] = "2 非常简单";
        RanzomierMenuTranslations["3 easy"] = "3 简单";
        RanzomierMenuTranslations["4 normal"] = "4 正常";
        RanzomierMenuTranslations["5 normal"] = "5 正常";
        RanzomierMenuTranslations["6 normal"] = "6 正常";
        RanzomierMenuTranslations["7 hard"] = "7 困难";
        RanzomierMenuTranslations["8 hard"] = "8 困难";
        RanzomierMenuTranslations["9 very hard"] = "9 非常困难";
        RanzomierMenuTranslations["10 evil"] = "10 噩梦";

        // items
        RanzomierMenuTranslations["off"] = "关";
        RanzomierMenuTranslations["Unique Items are random"] = "独特物品随机";
        RanzomierMenuTranslations["Keys are random"] = "钥匙随机";
        RanzomierMenuTranslations["Shop currency is random"] = "商店货币随机";
        RanzomierMenuTranslations["All Item uses are random"] = "所有物品和用途随机";

        // areas
        RanzomierMenuTranslations["main areas"] = "主区域";
        RanzomierMenuTranslations["all areas"] = "所有区域";
    }

    private static string InsertManualBreaks(string text, int maxWidth)
    {
        StringBuilder sb = new();
        float currentX = 0;
        int newLineIndex = -1;
        bool inTag = false;

        for (int i = 0; i < text.Length; i++)
        {
            char c = text[i];

            if (c == '\n' || c == '\r')
            {
                currentX = 0;
                newLineIndex = -1;
                inTag = false;
                sb.Append(c);
                continue;
            }

            if (
                c == '<'
                && i + 1 < text.Length
                && (char.IsLetter(text[i + 1]) || text[i + 1] == '/')
            )
            {
                inTag = true;
                sb.Append(c);
                continue;
            }

            if (inTag && c == '>')
            {
                inTag = false;
                sb.Append(c);
                int len = sb.Length;
                if (len >= 4 && sb[len - 4] == '<' && sb[len - 3] == 'b' && sb[len - 2] == 'r')
                {
                    currentX = 0;
                    newLineIndex = -1;
                }
                continue;
            }

            if (inTag)
            {
                sb.Append(c);
                continue;
            }

            if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && !(c >= '0' && c <= '9'))
            {
                newLineIndex = i;
            }

            if (c == '[' || c == ']')
            {
                sb.Append(c);
                continue;
            }

            // ASCII characters are 1 unit wide, non-ASCII characters are 2 units wide
            int charW = c >= 0 && c <= 127 ? 1 : 2;

            if (currentX > 0 && currentX + charW > maxWidth)
            {
                currentX = 0;
                if (newLineIndex != -1)
                {
                    int charsToRemove = i - newLineIndex;
                    sb.Length -= charsToRemove;
                    sb.Append('\n');
                    i = newLineIndex - 1;
                    newLineIndex = -1;
                    continue;
                }
                sb.Append('\n');
                newLineIndex = -1;
            }

            sb.Append(c);
            currentX += charW;
        }

        return sb.ToString();
    }
}
