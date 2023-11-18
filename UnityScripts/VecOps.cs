using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class VecOps 
{
    public static float Dot( Vector3 a, Vector3 b )
    {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    public static float Magnitude( Vector3 v )
    {
        return Mathf.Sqrt( v.x*v.x + v.y*v.y + v.z*v.z );
    }

    public static Vector3 Unitary( Vector3 v )
    {
        float vm = Magnitude( v );
        return new Vector3( v.x/vm, v.y/vm, v.z/vm );
    }

    public static float Angle( Vector3 a, Vector3 b )
    {
        Vector3 ua = Unitary( a );
        Vector3 ub = Unitary( b );
        return Mathf.Acos(Dot( ua, ub ) );
    }

    public static Vector3 Cross( Vector3 a, Vector3 b )
    {
        Vector3 cross = new Vector3(0,0,0);
        cross.x = a.y * b.z - a.z * b.y;
        cross.y = a.z * b.x - a.x * b.z;
        cross.z = a.x * b.y - a.y * b.x;
        return cross;
    }

    public static Matrix4x4 TranslateM(float dx, float dy, float dz)
    {
        Matrix4x4 tm = Matrix4x4.identity;
        tm[0,3] = dx;
        tm[1,3] = dy;
        tm[2,3] = dz;

        return tm;
    }
    
    public static Matrix4x4 ScaleM(float sx, float sy, float sz)
    {
        Matrix4x4 sm = Matrix4x4.identity;
        sm[0,0] = sx;
        sm[1,1] = sy;
        sm[2,2] = sz;

        return sm;
    }

    public static Matrix4x4 RotateX(float degrees)
    {   
        float rad = degrees * Mathf.Deg2Rad;
        Matrix4x4 rx = Matrix4x4.identity;
        float cos = Mathf.Cos(rad);
        float sin = Mathf.Sin(rad);
        
        rx[1,1] = cos;
        rx[1,2] = -sin;
        rx[2,1] = sin;
        rx[2,2] = cos;

        return rx;
    }

    public static Matrix4x4 RotateY(float degrees)
    {   
        float rad = degrees * Mathf.Deg2Rad;
        Matrix4x4 ry = Matrix4x4.identity;
        float cos = Mathf.Cos(rad);
        float sin = Mathf.Sin(rad);

        ry[0,0] = cos;
        ry[0,2] = sin;
        ry[2,0] = -sin;
        ry[2,2] = cos;

        return ry;
    }

    public static Matrix4x4 RotateZ(float degrees)
    {
        float rad = degrees * Mathf.Deg2Rad;
        Matrix4x4 rz = Matrix4x4.identity;
        float cos = Mathf.Cos(rad);
        float sin = Mathf.Sin(rad);

        rz[0,0] = cos;
        rz[0,1] = -sin;
        rz[1,0] = sin;
        rz[1,1] = cos;

        return rz;
    }

    public static List<Vector3> ApplyTransform(List<Vector3> originals, Matrix4x4 m)
    {
        List<Vector3> result = new List<Vector3>();
        foreach(Vector3 o in originals) // When no GPU :(
        {
            Vector4 temp = new Vector4(o.x, o.y, o.z,1);
            temp = m * temp;
            result.Add(temp);
        }
        return result;
    }
}
