
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

using IHost host = Host.CreateDefaultBuilder(args).Build();

const bool SIMILAR = true;
const bool GROUP = true;
const bool FACELIST = true;
const bool INTEGRATION = true;

// Ask the service provider for the configuration abstraction.
IConfiguration config = host.Services.GetRequiredService<IConfiguration>();
FacesMgr faceOps = new FacesMgr(config);

if (FACELIST)
{
    Console.WriteLine("Testing FaceList");
    var tests = new Tests(config);
    tests.TestCleanup();
    tests.TestAddedFaces();
}

if (GROUP)
{
    Console.WriteLine("Testing Grouping");
    var testsGroup = new Tests(config);
    testsGroup.TestCleanup();
    testsGroup.TestGetGroups_FromFaceList();

}

if (SIMILAR)
{
    Console.WriteLine("Testing SimilarFaces Detection");
    var testsGroup = new Tests(config);
    testsGroup.TestCleanup();
    testsGroup.Test_Similar();
}


if (INTEGRATION)
{
    var testsGroup = new Tests(config);
    testsGroup.TestCleanup();

    var redis = new RedisAccess(config);
    var halloweenFace = new HalloweenFaces(config);

    // Get all the faces from the database.
    var redisFaces = redis.GetImages().ToList();

    foreach (var face in redisFaces)
    {
        var invalid = halloweenFace.AddFaceAndGroup(face).GetAwaiter().GetResult();
        if (invalid != null)
        {
            Console.WriteLine($"Invalid Face: {invalid.face_id}");
        }
    }
    //Utils.SaveGroupImagesToFS(halloweenFace, redisFaces);
}
await host.RunAsync();

