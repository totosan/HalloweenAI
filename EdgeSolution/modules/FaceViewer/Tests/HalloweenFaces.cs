using Microsoft.Azure.CognitiveServices.Vision.Face.Models;
using Microsoft.Extensions.Configuration;
using System.Text.Json;

public class HalloweenFaces
{
    private FacesMgr faceOps;
    private List<PersistedFace> _storedFaces;
    public List<PersistedFace> StoredFaces
    {
        get
        {
            return _storedFaces;
        }
    }

    public List<DetectedFace> DetectedFaces { get; set; }

    public PersistedFace RecentAddedFace { get; set; }
    public List<List<Guid>> Groups { get; set; } = new List<List<Guid>>();

    public HalloweenFaces(IConfiguration config)
    {
        faceOps = new FacesMgr(config);
        faceOps.CreateIfNotExistsFaceListAsync().Wait();
        _storedFaces = faceOps.GetFacesFromFaceListAsync().Result.ToList();
        this.DetectedFaces = new List<DetectedFace>();
    }
    public async Task InitFaceList()
    {
        await faceOps.DeleteFaceListAsync();
        await faceOps.CreateIfNotExistsFaceListAsync();
        _storedFaces = new List<PersistedFace>();
    }

    public async Task<GroupResult> GetGroupsWithFaceDetection(IList<RedisRecord> recordOfFaces)
    {
        var detectedFaces = await faceOps.DetectedFaceAsync(recordOfFaces);
        return await faceOps.GroupFacesAsync(detectedFaces.Select(x => x.FaceId.Value).ToList());
    }
    public async Task<GroupResult> GetGroupsBy24Detection()
    {
        return await faceOps.GroupFacesAsync(DetectedFaces.Select(x => x.FaceId.Value).ToList());
    }
    internal async Task<IList<SimilarFace>> GetSimilarFaces(RedisRecord redisFace, bool faceList = true)
    {
        var detected = await faceOps.DetectedFaceAsync(new List<RedisRecord>() { redisFace });

        IList<SimilarFace> result = new List<SimilarFace>();

        if (detected != null)
        {
            if (faceList)
            {
                result = await faceOps.GetSimilarFacesFromListAsync(detected[0].FaceId.Value);
            }
            else
            {
                result = await faceOps.GetSimilarFacesAsync(detected.SingleOrDefault().FaceId.Value, DetectedFaces.Select(x => x.FaceId).ToList());
            }
        }
        return result;
    }
    internal async Task<IList<SimilarFace>> GetSimilarFaces(DetectedFace detected, bool faceList = true)
    {
        IList<SimilarFace> result = new List<SimilarFace>();

        if (detected != null)
        {
            if (faceList)
            {
                result = await faceOps.GetSimilarFacesFromListAsync(detected.FaceId.Value);
            }
            else
            {
                result = await faceOps.GetSimilarFacesAsync(detected.FaceId.Value, DetectedFaces.Select(x => x.FaceId).ToList());
            }
        }
        return result;
    }

    public async Task<RedisRecord?> AddFace(RedisRecord face)
    {
        var invalidFaceRecord = await faceOps.AddFacesToFaceListAsync(new List<RedisRecord> { face });
        Task.Delay(50).Wait();
        var facesAdded = await faceOps.GetFacesFromFaceListAsync();
        _storedFaces.Clear();
        _storedFaces.AddRange(facesAdded);
        this.RecentAddedFace = facesAdded.Last();

        if (invalidFaceRecord.Count == 1)
        {
            return invalidFaceRecord.First();
        }
        else
            return null;
    }

    /// <summary>
    /// Addes a face to FaceAPI FaceList and forms a group of similar faces
    /// </summary>
    /// <param name="face">RedisRecord face</param>
    /// <returns>No valid face</returns>
    public async Task<RedisRecord?> AddFaceAndGroup(RedisRecord face)
    {
        var detectedFace = await faceOps.DetectedFaceAsync(new List<RedisRecord> { face });
        if (detectedFace.Any())
        {
            this.DetectedFaces.Add(detectedFace.First());

            var similar = await GetSimilarFaces(detectedFace.SingleOrDefault(), faceList: false);
            if (similar.Any() && similar.Count > 1)
            {
                var invalidFaceRecord = await faceOps.AddFacesToFaceListAsync(new List<RedisRecord> { face });
                var facesAdded = await faceOps.GetFacesFromFaceListAsync();

                List<Guid> similarFaceIds = similar.Where(s => s.FaceId.HasValue).Select(s => s.FaceId.Value).ToList();

                if (this.Groups.Any())
                {
                    // is there a group that exists completely in similarFaceIds? 
                    var groupMatch = this.Groups.Where(g => g.All(s => similarFaceIds.Contains(s))).SingleOrDefault();
                    if (groupMatch != null)
                    {
                        groupMatch.Add(detectedFace.SingleOrDefault().FaceId.Value);
                    }
                    else
                    {
                        this.Groups.Add(similarFaceIds);
                    }
                }
                else
                {
                    this.Groups.Add(similarFaceIds);
                }
            }
        }else{
            return face;
        }
        return null;
    }

    public void 
}
