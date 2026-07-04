using System;
using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEngine;

namespace RhellHan;

public class TranslationRow
{
    public List<string> TranslationKey { get; set; }
    public string TranslationOriginalText { get; set; }
    public string TranslationTranslatedText { get; set; }
}

public static class ResourceLoader
{
    private const string translationFilePath = "resources";

    // private static readonly Dictionary<string, TMP_FontAsset> _cachedChineseFonts =
    //     new Dictionary<string, TMP_FontAsset>();
    private static AssetBundle _cachedFontBundle = null;

    public static TMP_FontAsset LoadChineseFont(string bundleName, string fontAssetName)
    {
        string cacheKey = $"{bundleName}|||{fontAssetName}";
        if (_cachedFontBundle != null)
        {
            var loadedBundle = _cachedFontBundle.LoadAsset(fontAssetName, typeof(TMP_FontAsset));
            if (loadedBundle != null)
            {
                return loadedBundle as TMP_FontAsset;
            }
        }

        var bundlePath = System.IO.Path.Combine(
            BepInEx.Paths.PluginPath,
            translationFilePath,
            bundleName
        );

        Plugin.Logger.LogInfo($"Loading font bundle from: {bundlePath}");

        if (!File.Exists(bundlePath))
        {
            Plugin.Logger.LogError($"Font bundle file not found: {bundlePath}");
            return null;
        }

        var fontBundle = AssetBundle.LoadFromFile(bundlePath);
        if (fontBundle == null)
        {
            Plugin.Logger.LogError($"Failed to load font asset bundle: {bundleName}");
            return null;
        }

        // List all asset names for debugging
        var allNames = fontBundle.GetAllAssetNames();
        foreach (var n in allNames)
            Plugin.Logger.LogInfo($"  Bundle contains asset: {n}");

        var loaded =
            fontBundle.LoadAsset(fontAssetName, typeof(TMP_FontAsset))
            ?? fontBundle.LoadAsset("KNMaiyuan-Regular", typeof(TMP_FontAsset));

        // Try alternative names

        if (loaded == null)
        {
            Plugin.Logger.LogError("Failed to load Xiaolai-Regular SDF from bundle!");
            return null;
        }

        var chineseFont = loaded as TMP_FontAsset;
        _cachedFontBundle = fontBundle;
        Plugin.Logger.LogInfo("Successfully loaded Xiaolai-Regular font");
        return chineseFont;
    }

    public static Font LoadChineseFontAsUITextFont(string bundleName, string fontAssetName)
    {
        if (_cachedFontBundle != null)
        {
            var loadedBundle = _cachedFontBundle.LoadAsset(fontAssetName, typeof(Font));
            if (loadedBundle != null)
            {
                return loadedBundle as Font;
            }
        }
        var bundlePath = System.IO.Path.Combine(
            BepInEx.Paths.PluginPath,
            translationFilePath,
            bundleName
        );

        Plugin.Logger.LogInfo($"Loading font bundle from: {bundlePath}");

        if (!File.Exists(bundlePath))
        {
            Plugin.Logger.LogError($"Font bundle file not found: {bundlePath}");
            return null;
        }

        var fontBundle = AssetBundle.LoadFromFile(bundlePath);
        if (fontBundle == null)
        {
            Plugin.Logger.LogError($"Failed to load font asset bundle: {bundleName}");
            return null;
        }

        // List all asset names for debugging
        var allNames = fontBundle.GetAllAssetNames();
        foreach (var n in allNames)
            Plugin.Logger.LogInfo($"  Bundle contains asset: {n}");

        var loaded = fontBundle.LoadAsset(fontAssetName, typeof(Font));
        var chineseFont = loaded as Font;
        _cachedFontBundle = fontBundle;
        Plugin.Logger.LogInfo("Successfully loaded font");
        return chineseFont;
    }

    public static IEnumerable<TranslationRow> GetTranslationRows(
        string fileName,
        int expectedKeyCount = int.MinValue
    )
    {
        var filePath = Path.Combine(BepInEx.Paths.PluginPath, translationFilePath, fileName);
        if (!File.Exists(filePath))
        {
            Plugin.Logger.LogError($"Translation file not found: {filePath}");
            yield break;
        }

        var allText = File.ReadAllText(filePath).Replace("\uFEFF", "");
        var rows = ParseCsvRows(allText);
        foreach (var values in rows)
        {
            if (values.Count == 2)
                values.Add(values[1]);
            if (values.Count < 3)
                continue;

            var keysText = values[0];
            var keys = string.IsNullOrEmpty(keysText)
                ? new List<string>()
                : new List<string>(keysText.Split(new[] { "|||" }, StringSplitOptions.None));
            if (keys.Count < expectedKeyCount)
                continue;

            yield return new TranslationRow
            {
                TranslationKey = keys,
                TranslationOriginalText = values[1],
                TranslationTranslatedText = values[2],
            };
        }
    }

    private static List<List<string>> ParseCsvRows(string text)
    {
        var rows = new List<List<string>>();
        var currentRow = new List<string>();
        var currentField = "";
        var inQuotes = false;

        for (int i = 0; i < text.Length; i++)
        {
            var ch = text[i];
            if (ch == '\"')
            {
                if (inQuotes && i + 1 < text.Length && text[i + 1] == '\"')
                {
                    currentField += '\"';
                    i++;
                }
                else
                {
                    inQuotes = !inQuotes;
                }
            }
            else if (ch == ',' && !inQuotes)
            {
                currentRow.Add(currentField);
                currentField = "";
            }
            else if ((ch == '\r' || ch == '\n') && !inQuotes)
            {
                if (ch == '\r' && i + 1 < text.Length && text[i + 1] == '\n')
                    i++;
                if (currentRow.Count > 0 || currentField.Length > 0)
                {
                    currentRow.Add(currentField);
                    rows.Add(currentRow);
                    currentRow = new List<string>();
                    currentField = "";
                }
            }
            else
            {
                currentField += ch;
            }
        }

        if (currentRow.Count > 0 || currentField.Length > 0)
        {
            currentRow.Add(currentField);
            rows.Add(currentRow);
        }

        return rows;
    }
}
