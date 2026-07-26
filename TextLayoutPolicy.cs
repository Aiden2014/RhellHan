namespace RhellHan;

internal static class TextLayoutPolicy
{
    internal const float AutomaticChineseDialogueFontSizeMax = 80f;

    internal static string PrepareDescription(string translatedText)
    {
        return translatedText;
    }

    internal static float GetDialogueFontSizeMax(
        string text,
        float authoredFontSize,
        float gameFontSizeMax
    )
    {
        if (authoredFontSize == 0f && ContainsChinese(text))
        {
            return AutomaticChineseDialogueFontSizeMax;
        }

        return gameFontSizeMax;
    }

    private static bool ContainsChinese(string text)
    {
        if (string.IsNullOrEmpty(text))
        {
            return false;
        }

        for (int i = 0; i < text.Length; i++)
        {
            if (text[i] >= 0x4E00 && text[i] <= 0x9FFF)
            {
                return true;
            }
        }

        return false;
    }
}
