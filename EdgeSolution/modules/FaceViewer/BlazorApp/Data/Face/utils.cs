using System.Drawing;

public class Utils
{
    public static Image ConvertBase64ToImage(string base64String)
    {
        // Convert Base64 String to byte[]
        byte[] imageBytes = Convert.FromBase64String(base64String);
        MemoryStream ms = new MemoryStream(imageBytes, 0, imageBytes.Length);
        // Convert byte[] to Image
        ms.Write(imageBytes, 0, imageBytes.Length);
        Image image = Image.FromStream(ms, true);
        return image;
    }

    public static void SaveImage(Image image, string path)
    {
        image.Save(path);
    }

public static void SaveGroupImagesToFS(HalloweenFaces halloweenFace, List<RedisRecord> redisFaces)
{
    if (!Directory.Exists("images/groups"))
    {
        Directory.CreateDirectory("images/groups");
    }
    for (int i = 0; i < halloweenFace.Groups.Count; i++)
    {
        if (!Directory.Exists($"images/groups/{i}"))
            Directory.CreateDirectory($"images/groups/{i}");

        foreach (var face in halloweenFace.Groups[i])
        {
            Utils.SaveImage(Utils.ConvertBase64ToImage(redisFaces.Single(f => f.face_id == face.ToString()).img), $"images/groups/{i}/{face}.jpg");
        }
    }
}

public static void SaveRedisImages(List<RedisRecord> redisFaces)
{
    if (!Directory.Exists("images/redis"))
    {
        Directory.CreateDirectory("images/redis");
        foreach (var face in redisFaces)
        {
            Utils.SaveImage(Utils.ConvertBase64ToImage(face.img), $"images/redis/{face.face_id}.jpg");
        }
    }
}
}