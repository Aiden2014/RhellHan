using System.Text;

namespace RhellHan;

internal static class TextLayoutPolicy
{
    internal const float AutomaticChineseDialogueFontSizeMax = 80f;
    internal const int InventoryMenuDescriptionWidth = 50;

    internal static string PrepareDescription(string translatedText)
    {
        return translatedText;
    }

    internal static string PrepareInventoryMenuDescription(string text)
    {
        return InsertManualBreaks(text, InventoryMenuDescriptionWidth);
    }

    internal static string InsertManualBreaks(string text, int maxWidth)
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
