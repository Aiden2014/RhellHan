using System;
using System.Collections.Generic;
using System.Linq;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace RhellHan;

public class FallbackFontThicknessFixer : MonoBehaviour
{
    private void Update()
    {
        var subMeshes = GetComponentsInChildren<TMP_SubMeshUI>();
        foreach (var sm in subMeshes)
        {
            if (sm.sharedMaterial?.HasProperty(ShaderUtilities.ID_FaceDilate) == true)
            {
                if (ShaderUtilities.ID_FaceDilate != -0.15f)
                {
                    sm.sharedMaterial.SetFloat(ShaderUtilities.ID_FaceDilate, -0.15f);
                }
            }
        }
    }
}

[BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin
{
    internal static new ManualLogSource Logger;

    public static ConfigEntry<int> _targetFps;

    private void Awake()
    {
        // Plugin startup logic
        Logger = base.Logger;
        TranslationManager.Init();
        _targetFps = Config.Bind("Graphics", "TargetFPS", -1, "target frame rate limit");
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = _targetFps.Value;
        Logger.LogInfo($"Plugin {MyPluginInfo.PLUGIN_GUID} is loaded!");
        Harmony.CreateAndPatchAll(typeof(Hooks));
    }
}

public static class Hooks
{
    // [HarmonyPatch(typeof(DialogueUI), nameof(DialogueUI.SetDialogueSection))]
    // [HarmonyPostfix]
    // public static void DialogueUI_SetDialogueSection_Postfix(
    //     ref List<DialogueSegment> ___currentDialogue,
    //     int dex
    // )
    // {
    //     Plugin.Logger.LogInfo("DialogueUI.SetDialogueSection called");

    //     var segments = ___currentDialogue;

    //     if (segments == null || segments.Count == 0)
    //     {
    //         return;
    //     }
    //     var dialogueKey = string.Join("|||", segments.Select(s => s.dialogue));
    //     Plugin.Logger.LogInfo($"Original dialogue key: {dialogueKey}");
    //     if (
    //         TranslationManager.DialogueTranslations.TryGetValue(dialogueKey, out var translatedList)
    //     )
    //     {
    //         for (int i = 0; i < segments.Count && i < translatedList.Count; i++)
    //         {
    //             Plugin.Logger.LogInfo(
    //                 $"Translating segment {i}: '{segments[i].dialogue}' to '{translatedList[i]}'"
    //             );
    //             segments[i].dialogue = translatedList[i];
    //         }
    //     }
    //     else
    //     {
    //         Plugin.Logger.LogWarning($"No translation found for dialogue key: {dialogueKey}");
    //     }

    //     // if (__instance.dialogueBox.text.Contains("During that time"))
    //     // {
    //     //     __instance.dialogueBox.text = "Sorry again for that.";
    //     // }
    //     // __instance.dialogueBox.font.fallbackFontAssetTable.Add(
    //     //     ResourceLoader.LoadChineseFont("chinese_font_daydream.bundle", "KN Maiyuan Daydream")
    //     // );
    //     // // Plugin.ExportDialogues();
    // }

    [HarmonyPatch(typeof(DialogueUI), nameof(DialogueUI.FeedDialouge))]
    [HarmonyPrefix]
    public static void DialogueUI_FeedDialouge_Prefix(
        DialogueUI __instance,
        ref List<DialogueSegment> segments
    )
    {
        Plugin.Logger.LogInfo(
            "DialogueUI.FeedDialouge called with " + (segments?.Count ?? 0) + " segments"
        );

        if (segments == null || segments.Count == 0)
        {
            return;
        }
        var dialogueKey = string.Join("|||", segments.Select(s => s.dialogue));
        Plugin.Logger.LogInfo($"Original dialogue key: {dialogueKey}");
        if (
            TranslationManager.DialogueTranslations.TryGetValue(dialogueKey, out var translatedList)
        )
        {
            for (int i = 0; i < segments.Count && i < translatedList.Count; i++)
            {
                Plugin.Logger.LogInfo(
                    $"Translating segment {i}: '{segments[i].dialogue}' to '{translatedList[i]}'"
                );
                segments[i].dialogue = translatedList[i];
            }
        }
        else
        {
            var anyTranslated = false;
            for (int i = 0; i < segments.Count; i++)
            {
                if (
                    TranslationManager.RoomHintTranslations.TryGetValue(
                        segments[i].dialogue,
                        out var translated
                    )
                )
                {
                    segments[i].dialogue = translated;
                    anyTranslated = true;
                }
            }
            if (!anyTranslated)
            {
                Plugin.Logger.LogWarning($"No translation found for dialogue key: {dialogueKey}");
            }
        }

        // 检查是否有中文字符，如果有则挂载字体厚度修复组件
        var hasChinese = segments.Any(s => s.dialogue.Any(c => isChineseChar(c)));
        if (
            hasChinese
            && __instance.dialogueBox.gameObject.GetComponent<FallbackFontThicknessFixer>() == null
        )
        {
            __instance.dialogueBox.gameObject.AddComponent<FallbackFontThicknessFixer>();
        }
    }

    [HarmonyPatch(typeof(TMP_FontAsset), nameof(TMP_FontAsset.ReadFontAssetDefinition))]
    [HarmonyPostfix]
    public static void TMP_FontAsset_ReadFontAssetDefinition_Postfix(TMP_FontAsset __instance)
    {
        if (__instance == null || __instance.name == null)
        {
            return;
        }
        var chineseFallbackFont = ResourceLoader.LoadChineseFont(
            "chinese_font.bundle",
            "KNMaiyuan SDF"
        // "mao_ken.bundle",
        // "MaoKen0"
        );
        FontManager.SaveFallbackFont(__instance, chineseFallbackFont);
    }

    [HarmonyPatch(typeof(PlayerInventory), nameof(PlayerInventory.FillValueFromSaveFile))]
    [HarmonyPostfix]
    public static void PlayerInventory_FillValueFromSaveFile_Postfix(PlayerInventory __instance)
    {
        Plugin.Logger.LogInfo("PlayerInventory.FillValueFromSaveFile called");

        TranslateByIndex(
            ref __instance.RuneIndex,
            TranslationManager.RuneNameTranslations,
            (item, name) => item.Name = name
        );
        TranslateByIndex(
            ref __instance.RuneIndex,
            TranslationManager.RuneDescriptionTranslations,
            (item, desc) => item.Description = desc
        );
        TranslateByIndex(
            ref __instance.ItemIndex,
            TranslationManager.ItemNameTranslations,
            (item, name) => item.Name = name
        );
        TranslateByIndex(
            ref __instance.ItemIndex,
            TranslationManager.ItemDescriptionTranslations,
            (item, desc) => item.Description = desc
        );
    }

    [HarmonyPatch(typeof(UISelectableSpell), nameof(UISelectableSpell.GetDescription))]
    [HarmonyPostfix]
    public static void UISelectableSpell_GetDescription_Postfix(
        UISelectableSpell __instance,
        ref string __result
    )
    {
        Plugin.Logger.LogInfo(
            $"Getting description for spell: {__instance.name}, original description: {__result}"
        );
        // __result = "这是一个技能描述的示例。";
    }

    [HarmonyPatch(typeof(UiStoryHandle), nameof(UiStoryHandle.ActivateStoryPoint))]
    [HarmonyPrefix]
    public static void UiStoryHandle_ActivateStoryPoint_Prefix(UiStoryHandle __instance)
    {
        if (__instance.summaries.Any(s => s.storyTxt.Any(c => isChineseChar(c))))
            return;

        var summaryKey = string.Join("|||", __instance.summaries.Select(s => s.storyTxt));
        if (string.IsNullOrEmpty(summaryKey))
            return;

        if (TranslationManager.SummaryTranslations.TryGetValue(summaryKey, out var translatedList))
        {
            for (int i = 0; i < __instance.summaries.Count && i < translatedList.Count; i++)
                __instance.summaries[i].storyTxt = translatedList[i];
        }
    }

    [HarmonyPatch(typeof(UIBehaviour), "Start")]
    [HarmonyPrefix]
    public static void TMP_Text_set_text_Prefix(UIBehaviour __instance)
    {
        if (__instance is Text textComponent)
        {
            if (
                string.IsNullOrEmpty(textComponent.text)
                || textComponent.text.Any(c => isChineseChar(c))
            )
            {
                return;
            }
            var normalizedText = TranslationManager.NormalizeNewlines(textComponent.text);
            if (
                TranslationManager.TextTranslations.TryGetValue(
                    normalizedText,
                    out var translatedText
                )
            )
            {
                var chineseFont = ResourceLoader.LoadChineseFontAsUITextFont(
                    "chinese_font.bundle",
                    "Ui_Font_02_KNMaiyuan"
                // "mao_ken.bundle",
                // "MaoKen0"
                );
                textComponent.font = chineseFont;
                textComponent.text = translatedText;
                if (!textComponent.font.ToString().Equals("Ui_Font_02 (UnityEngine.Font))"))
                {
                    Plugin.Logger.LogWarning(
                        $"{textComponent.font}) is not Ui_Font_02, value: {textComponent.text}, translated: {translatedText}"
                    );
                }
            }
            else
            {
                Plugin.Logger.LogWarning($"No translation found for text: {textComponent.text}");
            }
        }
    }

    [HarmonyPatch(typeof(Text), nameof(Text.text), MethodType.Setter)]
    [HarmonyPrefix]
    public static void Text_set_text_Prefix(Text __instance, string value)
    {
        if (string.IsNullOrEmpty(value) || !value.Any(c => isChineseChar(c)))
        {
            return;
        }
        if (!__instance.font.name.Equals("Ui_Font_02_KNMaiyuan"))
        {
            Plugin.Logger.LogInfo(
                $"Text_set_text_Prefix: font is {__instance.font.name}, value: {value}"
            );
            __instance.font = ResourceLoader.LoadChineseFontAsUITextFont(
                "chinese_font.bundle",
                "Ui_Font_02_KNMaiyuan"
            // "mao_ken.bundle",
            // "MaoKen0"
            );
        }
    }

    [HarmonyPatch(typeof(PauseBeesleHints), nameof(PauseBeesleHints.SetupText))]
    [HarmonyPrefix]
    public static void PauseBeesleHints_SetupText_Prefix(PauseBeesleHints __instance)
    {
        if (__instance.hints.Any(h => h.hintText.Any(c => isChineseChar(c))))
        {
            return;
        }
        TranslateByIndex(
            ref __instance.hints,
            TranslationManager.HintTranslations,
            (hint, text) => hint.hintText = text
        );
        TranslateByIndex(
            ref __instance.demohints,
            TranslationManager.DemoHintTranslations,
            (hint, text) => hint.hintText = text
        );
    }

    [HarmonyPatch(typeof(MapHandle), nameof(MapHandle.UpdateLocationDescription))]
    [HarmonyPrefix]
    public static void MapHandle_UpdateLocationDescription_Prefix(
        ref string desc,
        ref GameObject root
    )
    {
        if (
            TranslationManager.MapLocationHightlightTranslations.TryGetValue(
                desc,
                out var translation
            )
        )
        {
            Plugin.Logger.LogInfo($"Translated map location highlight: {desc}");
            desc = translation;
            return;
        }
        Plugin.Logger.LogWarning($"No translation found for map location highlight: {desc}");
    }

    [HarmonyPatch(typeof(DialogueUI), nameof(DialogueUI.DoesHaveDialogueChoices))]
    [HarmonyPostfix]
    public static void DialogueUI_DoesHaveDialogueChoices_Postfix(
        ref InteractDialogue currnet,
        ref bool __result
    )
    {
        if (!__result)
        {
            return;
        }
        var dialogueOptionsKey = string.Join(
            "|||",
            currnet.dialogueOptions.Select(o => o.optionText)
        );
        if (
            TranslationManager.DialogueOptionTranslations.TryGetValue(
                dialogueOptionsKey,
                out var dialogueOptions
            )
            && dialogueOptions.Count == currnet.dialogueOptions.Count
        )
        {
            for (int i = 0; i < currnet.dialogueOptions.Count; i++)
            {
                currnet.dialogueOptions[i].optionText = dialogueOptions[i];
            }
        }
        else
        {
            Plugin.Logger.LogWarning(
                $"No translation found for dialogue options key: {dialogueOptionsKey}"
            );
        }
    }

    [HarmonyPatch(typeof(DialogueChoiceHandle), nameof(DialogueChoiceHandle.FillChoices))]
    [HarmonyPostfix]
    public static void DialogueChoiceHandle_FillChoices_Postfix(DialogueChoiceHandle __instance)
    {
        float maxWidth = 200f;
        bool hasCjk = false;
        foreach (var option in __instance.allOptions)
        {
            if (option?.text == null)
                continue;
            var txt = option.text.text;
            if (!hasCjk && txt.Any(c => isChineseChar(c)))
                hasCjk = true;
            float width = option.text.GetPreferredValues(txt).x;
            if (width > maxWidth)
                maxWidth = width;
        }
        float cap = hasCjk ? 550f : 485f;
        if (maxWidth > cap)
        {
            maxWidth = cap;
        }
        __instance.handle.sizeDelta = new Vector2(maxWidth, __instance.handle.sizeDelta.y);
        foreach (var option in __instance.allOptions)
        {
            if (option != null)
            {
                option.rect.sizeDelta = new Vector2(maxWidth, 90f);
            }
        }
    }

    [HarmonyPatch(typeof(UiItemsHandle), nameof(UiItemsHandle.UpdateTab))]
    [HarmonyPostfix]
    public static void UiItemsHandle_UpdateTab_Postfix(UiItemsHandle __instance)
    {
        var text = __instance.itemDescription?.text;
        if (string.IsNullOrEmpty(text) || text.Any(c => isChineseChar(c)))
        {
            return;
        }
        if (TranslationManager.TabDescriptionTranslations.TryGetValue(text, out var translated))
        {
            __instance.itemDescription.text = translated;
        }
        else
        {
            Plugin.Logger.LogWarning($"No translation found for tab description: {text}");
        }
    }

    [HarmonyPatch(typeof(UiStoryCtrl), nameof(UiStoryCtrl.UpdateVisuals))]
    [HarmonyPostfix]
    public static void UiStoryCtrl_UpdateVisuals_Postfix(UiStoryCtrl __instance)
    {
        var text = __instance.StoryText?.text;
        if (string.IsNullOrEmpty(text) || text.Any(c => isChineseChar(c)))
            return;

        var trimmed = text.Trim();
        if (TranslationManager.StoryPointTranslations.TryGetValue(trimmed, out var translated))
        {
            __instance.StoryText.text = translated;
            return;
        }
        Plugin.Logger.LogWarning($"No translation found for story point text: {text}");

        // // Combined text from Setup() won't match individual CSV entries.
        // // Only split by "<br> <br>" (Setup's joiner), not "<br>" which can
        // // appear inside a single segment's text (e.g. Volcano Lab entry).
        // var parts = text.Split(new[] { "<br> <br>" }, StringSplitOptions.None);
        // var anyTranslated = false;
        // for (int i = 0; i < parts.Length; i++)
        // {
        //     var trimmed = parts[i].Trim();
        //     if (
        //         trimmed.Length > 0
        //         && TranslationManager.StoryPointTranslations.TryGetValue(trimmed, out var seg)
        //         && seg != trimmed
        //     )
        //     {
        //         parts[i] = seg;
        //         anyTranslated = true;
        //     }
        // }
        // if (anyTranslated)
        //     __instance.StoryText.text = string.Join("<br> <br>", parts);
    }

    private static readonly HashSet<WorldNames> _patchedWorldNames = [];

    private static void PatchWorldAreaNames(WorldNames worldNames)
    {
        if (worldNames?.worldAreaNames == null || !_patchedWorldNames.Add(worldNames))
            return;
        var translations = TranslationManager.WorldNameTranslations;
        for (int i = 0; i < worldNames.worldAreaNames.Count && i < translations.Count; i++)
            worldNames.worldAreaNames[i] = translations[i];
        Plugin.Logger.LogInfo($"Patched {worldNames.worldAreaNames.Count} world area names");
    }

    [HarmonyPatch(typeof(MainMenuUi), "Start")]
    [HarmonyPostfix]
    public static void MainMenuUi_Start_Postfix(MainMenuUi __instance)
    {
        var worldNames = Traverse.Create(__instance).Field<WorldNames>("worldNames").Value;
        PatchWorldAreaNames(worldNames);
    }

    [HarmonyPatch(typeof(MapHandle), nameof(MapHandle.SelectLocation))]
    [HarmonyPrefix]
    public static void MapHandle_SelectLocation_Prefix(MapHandle __instance)
    {
        var worldInfo = Traverse.Create(__instance).Field<WorldNames>("worldInfo").Value;
        PatchWorldAreaNames(worldInfo);
    }

    [HarmonyPatch(typeof(TextMeshPro), "Awake")]
    [HarmonyPrefix]
    public static void TextMeshPro_Awake_Prefix(TextMeshPro __instance)
    {
        // if (
        //     loadedFallbacks.TryGetValue(__instance.font.name, out var fallbackFont)
        // )
        // {
        //     ReplaceFont(__instance.font, fallbackFont);
        // }

        var normalizedTmpText = TranslationManager.NormalizeNewlines(__instance.text);
        if (
            TranslationManager.TextMeshProTranslations.TryGetValue(
                normalizedTmpText,
                out var translatedText
            )
        )
        {
            __instance.text = translatedText;
        }
    }

    [HarmonyPatch(typeof(UiItemsHandle), nameof(UiItemsHandle.BumpSortItems))]
    [HarmonyPostfix]
    public static void UiItemsHandle_BumpSortItems_Postfix(UiItemsHandle __instance)
    {
        UpdateSortText(__instance);
    }

    [HarmonyPatch(typeof(UiItemsHandle), nameof(UiItemsHandle.GenerateTabs))]
    [HarmonyPostfix]
    public static void UiItemsHandle_GenerateTabs_Postfix(
        PlayerInventory inventory,
        UiItemsHandle __instance
    )
    {
        UpdateSortText(__instance);
    }

    private static void UpdateSortText(UiItemsHandle __instance)
    {
        if (__instance.sortType == 0)
        {
            __instance.sortText.text = "排序：默认";
        }
        else if (__instance.sortType == 1)
        {
            __instance.sortText.text = "排序：字母顺序";
        }
        else if (__instance.sortType == 2)
        {
            __instance.sortText.text = "排序：数量";
        }
    }

    [HarmonyPatch(typeof(CheatRuneBook), nameof(CheatRuneBook.SetupCheatMenu))]
    [HarmonyPostfix]
    public static void CheatRuneBook_SetupCheatMenu_Postfix(CheatRuneBook __instance)
    {
        foreach (var cheatButton in __instance.cheatButtons)
        {
            if (
                TranslationManager.CheatTitleTranslations.TryGetValue(
                    cheatButton.cheatTitle,
                    out var translatedTitle
                )
            )
            {
                cheatButton.cheatTitle = translatedTitle;
            }
            else
            {
                Plugin.Logger.LogWarning(
                    $"No translation found for title: {cheatButton.cheatTitle}"
                );
            }

            if (
                TranslationManager.CheatDescriptionTranslations.TryGetValue(
                    cheatButton.cheatDescription,
                    out var translatedDescription
                )
            )
            {
                cheatButton.cheatDescription = translatedDescription;
            }
            else
            {
                Plugin.Logger.LogWarning(
                    $"No translation found for description: {cheatButton.cheatDescription}"
                );
            }
        }
    }

    [HarmonyPatch(typeof(ChallengeMenu), nameof(ChallengeMenu.SetupValues))]
    [HarmonyPrefix]
    public static void ChallengeMenu_SetupValues_Prefix(ChallengeMenu __instance)
    {
        foreach (var challenge in __instance.challenges)
        {
            if (
                TranslationManager.ChallengeMenuTranslations.TryGetValue(
                    challenge.ChallengeName,
                    out var translatedText
                )
            )
            {
                challenge.ChallengeName = translatedText;
            }
            else
            {
                Plugin.Logger.LogWarning(
                    $"No translation found for text: {challenge.ChallengeName}"
                );
            }
        }
    }

    [HarmonyPatch(typeof(UISelectableSpell), nameof(UISelectableSpell.GetTitle))]
    [HarmonyPostfix]
    public static void UISelectableSpell_GetTitle_Postfix(
        ref string __result,
        UISelectableSpell __instance
    )
    {
        if (
            !string.IsNullOrEmpty(__result)
            && !__result.Any(c => isChineseChar(c))
            && TranslationManager.SelectableSpellDescriptionTranslations.TryGetValue(
                __instance.runeDescription,
                out var translatedDescription
            )
        )
        {
            __instance.runeDescription = translatedDescription;
        }
        else
        {
            Plugin.Logger.LogWarning(
                $"No translation found for rune description: {__instance.runeDescription}"
            );
        }

        if (
            string.IsNullOrEmpty(__result)
            || __result.Any(c => isChineseChar(c))
            || "...".Equals(__result)
        )
        {
            return;
        }
        if (
            TranslationManager.SelectableSpellNameTranslations.TryGetValue(
                __result,
                out var translatedTitle
            )
        )
        {
            __result = translatedTitle;
        }
        else
        {
            Plugin.Logger.LogWarning($"No translation found for rune name: {__result}");
        }
    }

    private static bool isChineseChar(char c)
    {
        return c >= 0x4E00 && c <= 0x9FFF;
    }

    private static void TranslateByIndex<T>(
        ref List<T> arr,
        List<string> translations,
        Action<T, string> setNameAction
    )
    {
        var minCount = Math.Min(arr.Count, translations.Count);
        for (int i = 0; i < minCount; i++)
        {
            setNameAction(arr[i], translations[i]);
        }
        if (arr.Count != translations.Count)
        {
            Plugin.Logger.LogWarning(
                $"{nameof(translations)} count ({translations.Count}) does not match {nameof(arr)} count ({arr.Count})"
            );
        }
    }

    // public static void ReplaceFont(TMP_FontAsset __instance, TMP_FontAsset chineseFont)
    // {
    //     __instance.atlasTextures = chineseFont.atlasTextures;
    //     __instance.atlasWidth = chineseFont.atlasWidth;
    //     __instance.atlasHeight = chineseFont.atlasHeight;
    //     __instance.atlasPadding = chineseFont.atlasPadding;

    //     __instance.faceInfo = chineseFont.faceInfo;
    //     __instance.glyphTable = chineseFont.glyphTable;
    //     __instance.characterTable = chineseFont.characterTable;

    //     __instance.material.mainTexture = chineseFont.atlasTextures[0];

    //     __instance.fontWeights = chineseFont.fontWeights;

    //     if (chineseFont.fallbackFontAssetTable != null)
    //     {
    //         __instance.fallbackFontAssetTable = chineseFont.fallbackFontAssetTable;
    //     }
    // }
}
