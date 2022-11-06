using Microsoft.Extensions.Configuration;
using System.Text.Json;

partial class Tests
{
    public void TestAddedFaces()
    {
        if (redisFace != null)
        {
            var result = _faces.AddFace(redisFace).Result;
            if (result != null)
                Console.WriteLine($"Face {result.face_id} was not added");
            else
            {
                Console.WriteLine($"Face {redisFace.face_id} was added");
                var storedFaces = _faces.StoredFaces;
                if (storedFaces.SingleOrDefault() != null)
                    Console.WriteLine($"Face {redisFace.face_id} was added locally");
                else
                    Console.WriteLine($"Face {redisFace.face_id} was not added locally");
            }
        }
    }
}