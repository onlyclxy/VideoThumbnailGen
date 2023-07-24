using System;
using System.Diagnostics;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.IO;


namespace ImageMetadata
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                //其他平台可以去除这句
                MessageBox.Show("请拖到一个图片过来,或者传入图片路径作为参数", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                Console.WriteLine("请传入图片路径作为参数！");
                Console.WriteLine("按空格键退出...");
                Console.ReadKey();


                return;
            }

            string imagePath = args[0];

            try
            {
                string title = GetImageTitle(imagePath);
                Console.WriteLine("图片标题： " + title);

                if (File.Exists(title))
                {
                    OpenVideoPlayer(title);
                }
                else
                {
                    //其他平台可以去除这句
                    MessageBox.Show("图片关联的视频文件不存在: "+ title, "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    Console.WriteLine("图片关联的视频文件不存在: " + title);

                }

            }
            catch (Exception ex)
            {
                //其他平台可以去除这句
                MessageBox.Show("处理图片时出错：", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                Console.WriteLine("处理图片时出错：" + ex.Message);
                Console.WriteLine("按空格键退出...");
                Console.ReadKey();


            }
        }

        static string GetImageTitle(string imagePath)
        {
            using (var image = new Bitmap(imagePath))
            {
                var propertyItems = image.PropertyItems;
                foreach (var propItem in propertyItems)
                {
                    if (propItem.Id == 270) // 根据 EXIF 标签 ID 查找标题信息
                    {
                        string title = Encoding.UTF8.GetString(propItem.Value).TrimEnd('\0'); 

                        return title;


                    }
                }
            }

            return string.Empty;
        }
        static void OpenVideoPlayer(string videoPath)
        {
            // 这里假设默认的视频播放器可执行文件路径为 "C:\\Program Files\\VideoPlayer\\player.exe"
            //string playerPath = "C:\\Program Files\\VideoPlayer\\player.exe";

            Process.Start(videoPath);
        }
    }
}
