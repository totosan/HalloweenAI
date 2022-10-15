using System;
using Microsoft.Azure.CognitiveServices;
using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;
using Microsoft.Extensions.Options;

public class SimilarFace
{
    Guid? FaceId { get; set; }

    public SimilarFace(Guid? faceId)
    {
        FaceId = faceId;

        var faceKey = Environment.GetEnvironmentVariable("FACE_API_KEY");
        var faceEndpoint = Environment.GetEnvironmentVariable("FACE_API_ENDPOINT");
        var faceClient = new FaceClient(new ApiKeyServiceClientCredentials(faceKey)) { Endpoint = faceEndpoint };
    }

}