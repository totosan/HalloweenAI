using System;
using System.Drawing;
using Microsoft.Azure.CognitiveServices;
using Microsoft.Azure.CognitiveServices.Vision.Face;
using Microsoft.Azure.CognitiveServices.Vision.Face.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Options;

public class FacesMgr
{
    Guid? FaceId { get; set; }

    private const string FACELISTID = "halloween_01";
    IFaceClient Client;

    public FacesMgr(IConfiguration config)
    {
        var faceKey = Environment.GetEnvironmentVariable("FACE_API_KEY");
        var faceEndpoint = Environment.GetEnvironmentVariable("FACE_API_ENDPOINT");
        Client = new FaceClient(new ApiKeyServiceClientCredentials(faceKey)) { Endpoint = faceEndpoint };
    }

    public async Task<List<DetectedFace>> DetectedFaceAsync(IList<RedisRecord> sourceFaces)
    {
        IList<DetectedFace> targetFaces = new List<DetectedFace>();
        foreach (var face in sourceFaces)
        {
            // Detect faces from target image url.
            byte[] bytes = Convert.FromBase64String(face.img);

            using (MemoryStream ms = new MemoryStream(bytes))
            {
                var faces = await Client.Face.DetectWithStreamAsync(
                    ms,
                    true,
                    false,
                    new List<FaceAttributeType> { FaceAttributeType.HeadPose },
                    RecognitionModel.Recognition04,
                    false,
                    DetectionModel.Detection03);

                // Add detected faceId to targetFaceIds.
                if(faces.Any())
                {
                    face.face_id = faces[0].FaceId.Value.ToString();
                    targetFaces.Add(faces[0]);
                }
            }
        }

        return targetFaces.ToList();
    }

    public async Task<IList<SimilarFace>> GetSimilarFacesAsync(Guid faceId, IList<Guid?> compareList){
        var result = await Client.Face.FindSimilarAsync(
            faceId,
            null,
            null,
            compareList);
        return result;
    }

    public async Task<IList<SimilarFace>> GetSimilarFacesFromListAsync(Guid faceId){
        var result = await Client.Face.FindSimilarAsync(
            faceId,
            FACELISTID);
        return result;
    }

    // delete list of faceids from facelist
    public async Task DeleteFacesFromFaceListAsync(IList<Guid> faceIds)
    {
        foreach (var faceId in faceIds)
        {
            await Task.Delay(50);
            await Client.FaceList.DeleteFaceAsync(FACELISTID, faceId);
        }
    }

    // group faces
    public async Task<GroupResult> GroupFacesAsync(IList<Guid> faceIds)
    {
        var result = await Client.Face.GroupAsync(faceIds);
        return result;
    }

    // create a facelist
    public async Task CreateIfNotExistsFaceListAsync()
    {
        var faceList = await Client.FaceList.ListAsync();
        if ( faceList == null || !faceList.Any(x => x.FaceListId == FACELISTID))
        {
            await Client.FaceList.CreateAsync(FACELISTID, "HalloweenTest",recognitionModel: RecognitionModel.Recognition04);
        }
    }

    // add faces to facelist
    public async Task<IList<RedisRecord>> AddFacesToFaceListAsync(IList<RedisRecord> sourceFaces, string jsonMetaData=null)
    {
        List<RedisRecord> invalidFaces = new List<RedisRecord>();

        foreach (var face in sourceFaces)
        {
            // Detect faces from target image url.
            byte[] bytes = Convert.FromBase64String(face.img);

            using (MemoryStream ms = new MemoryStream(bytes))
            {
                try
                {
                    Task.Delay(50).Wait();
                    await Client.FaceList.AddFaceFromStreamAsync(FACELISTID,
                     ms,
                     userData: jsonMetaData,
                     detectionModel: DetectionModel.Detection03);
                }catch(APIErrorException ex)
                {
                    if(ex.Body.Error.Code == "InvalidImage")
                    {
                        Console.WriteLine($"InvalidImage of face {face.face_id}");
                        invalidFaces.Add(face);
                    }
                }
            }
        }

        return invalidFaces;
    }

    //get faces from facelist
    public async Task<IList<PersistedFace>> GetFacesFromFaceListAsync()
    {
        var faces = await Client.FaceList.GetAsync(FACELISTID);
        return faces.PersistedFaces;
    }

    public async Task DeleteFaceListAsync()
    {
        await Client.FaceList.DeleteAsync(FACELISTID);
    }
}