using Microsoft.Extensions.Configuration;
using System.Text.Json;

partial class Tests
{
    public void TestGetGroups_FromFaceList()
    {
        //Arrange        
        _faces.InitFaceList().Wait();

        //Act
        var groups = _faces.GetGroupsWithFaceDetection(new List<RedisRecord>{ redisFace,redisFace}).Result;

        //Assert
        if (groups.Groups.Count == 1)
        {
            if (groups.Groups[0].Count == 2)
            {
                Console.WriteLine("TestGetGroups_FromFaceList: Passed");
            }
        }
    }
}