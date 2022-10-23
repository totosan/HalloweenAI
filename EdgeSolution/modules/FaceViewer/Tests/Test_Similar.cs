using Microsoft.Azure.CognitiveServices.Vision.Face.Models;
using Microsoft.Extensions.Configuration;
using System.Text.Json;

partial class Tests
{
    public void Test_Similar()
    {
        //Arrange        
        _faces.InitFaceList().Wait();

        //Act
        var invalid = _faces.AddFace(redisFace).Result;
        if (invalid != null)
        {
            Console.WriteLine($"Invalid face: {invalid}");
        }
        
        var similar = _faces.GetSimilarFaces(redisFace).Result;

        if (similar.Count == 1)
        {
            Console.WriteLine("Test_Similar: Passed");
        }

    }
}