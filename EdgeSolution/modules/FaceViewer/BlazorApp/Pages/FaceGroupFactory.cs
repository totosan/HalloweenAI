using Microsoft.AspNetCore.Mvc;

public class FaceGroupFactory
{
    public void PutFaceId(string faceId)
    {
        Console.WriteLine("FaceId: " + faceId);
    }
}