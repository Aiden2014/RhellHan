namespace RhellHan;

internal static class Program
{
    private static int _failures;

    private static int Main()
    {
        Run(
            "long Chinese descriptions do not gain generated newlines",
            () =>
            {
                const string text =
                    "那个于你瞳孔深处颤动的黑色核心正透过模糊的视野凝视前方它被封装在宇宙那沉睡的汪洋中令那关于理解之顶点的提示如日落般隐没与此同时闪烁的大脑升腾入天际与创造之五手再度合而为一而那些本不该仰望星空之人的诅咒就在那里";
                Equal(text, TextLayoutPolicy.PrepareDescription(text));
                False(TextLayoutPolicy.PrepareDescription(text).Contains('\n'));
            }
        );

        Run(
            "authored newlines are preserved",
            () =>
            {
                const string text = "第一行\n第二行";
                Equal(text, TextLayoutPolicy.PrepareDescription(text));
            }
        );

        Run(
            "inventory menu wraps after twenty-five Chinese characters",
            () =>
            {
                Equal(
                    "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地人\n和",
                    TextLayoutPolicy.PrepareInventoryMenuDescription(
                        "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地人和"
                    )
                );
            }
        );

        Run(
            "inventory menu preserves authored newlines",
            () =>
            {
                Equal(
                    "第一行\n第二行",
                    TextLayoutPolicy.PrepareInventoryMenuDescription("第一行\n第二行")
                );
            }
        );

        Run(
            "inventory menu leaves short Chinese unchanged",
            () =>
            {
                Equal(
                    "简短中文",
                    TextLayoutPolicy.PrepareInventoryMenuDescription("简短中文")
                );
            }
        );

        Run(
            "inventory menu leaves short English unchanged",
            () =>
            {
                Equal(
                    "short English",
                    TextLayoutPolicy.PrepareInventoryMenuDescription("short English")
                );
            }
        );

        Run(
            "automatic Chinese dialogue can use the normal maximum",
            () =>
            {
                Equal(
                    80f,
                    TextLayoutPolicy.GetDialogueFontSizeMax("一幅画着大圆圈的符文图纸。", 0f, 55f)
                );
            }
        );

        Run(
            "explicit Chinese font size keeps the game maximum",
            () =>
            {
                Equal(42f, TextLayoutPolicy.GetDialogueFontSizeMax("中文", 42f, 42f));
            }
        );

        Run(
            "English dialogue keeps the game maximum",
            () =>
            {
                Equal(55f, TextLayoutPolicy.GetDialogueFontSizeMax("English dialogue", 0f, 55f));
            }
        );

        Run(
            "Chinese inside rich text uses the normal maximum",
            () =>
            {
                Equal(
                    80f,
                    TextLayoutPolicy.GetDialogueFontSizeMax(
                        "<color=#C7850F>抵消</color>魔法",
                        0f,
                        55f
                    )
                );
            }
        );

        return _failures;
    }

    private static void Run(string name, Action test)
    {
        try
        {
            test();
            Console.WriteLine($"PASS: {name}");
        }
        catch (Exception error)
        {
            _failures++;
            Console.Error.WriteLine($"FAIL: {name}: {error.Message}");
        }
    }

    private static void Equal<T>(T expected, T actual)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new InvalidOperationException($"expected '{expected}', got '{actual}'");
        }
    }

    private static void False(bool value)
    {
        if (value)
        {
            throw new InvalidOperationException("expected false, got true");
        }
    }
}
