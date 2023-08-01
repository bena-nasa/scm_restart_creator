from netCDF4 import Dataset
import numpy as np
import math as m

def convert_to_cart(lon,lat):
    cos_lat=np.cos(lat)
    return(
       np.cos(lon)*cos_lat,
       np.sin(lon)*cos_lat,
       np.sin(lat))

def lines_intersect(b0,b1,a0,a1):
    q=np.cross(b0,b1)
    p=np.cross(a0,a1)
    t=normal_vect(np.cross(p,q))
    s1=np.dot(np.cross(a0,p),t)
    s2=np.dot(np.cross(a1,p),t)
    s3=np.dot(np.cross(b0,q),t)
    s4=np.dot(np.cross(b1,q),t)
    signs=[]
    signs.append(-s1<0.0)
    signs.append(s2<0.0)
    signs.append(-s3<0.0)
    signs.append(s4<0.0)
    bool_array=np.array(signs)
    count=np.count_nonzero(bool_array)
    if (count==0) or (count==4):
       return 1
    else:
       return 0

def point_in_polygon(p0,pin,a1,a2,a3,a4):
    intersect=[]
    intersect.append(lines_intersect(p0,pin,a1,a2))
    intersect.append(lines_intersect(p0,pin,a2,a3))
    intersect.append(lines_intersect(p0,pin,a3,a4))
    intersect.append(lines_intersect(p0,pin,a4,a1))
    bool_array=np.array(intersect)
    count=np.count_nonzero(bool_array)
    if count%2==0:
       return 1
    else:
       return 0


def normal_vect(v):
    return v/np.sqrt(np.dot(v,v))
       
class Geolocation(object):

   def __init__(self,gridfile):
       ncFid = Dataset(gridfile, mode='r', format='NETCDF4')
       if ("nf" in ncFid.dimensions):
          self.lon_corners=ncFid.variables['corner_lons'][:]
          self.lat_corners=ncFid.variables['corner_lats'][:]
          self.lon=ncFid.variables['lons'][:]
          self.lat=ncFid.variables['lats'][:]
          self.npts=self.lon_corners.shape[1]
       elif ("grid_size" in ncFid.dimensions):
          self.npts = len(ncFid.dimensions['grid_size'])
          self.npts=self.npts//6
          self.npts=int(np.sqrt(self.npts))+1
          self.lon_corners=np.empty([6,self.npts,self.npts])
          self.lat_corners=np.empty([6,self.npts,self.npts])
          self.lon=np.empty([6,self.npts-1,self.npts-1])
          self.lat=np.empty([6,self.npts-1,self.npts-1])

          fsz = (self.npts-1)*(self.npts-1)
          noff = 0

          tmplon=ncFid.variables['grid_corner_lon'][:]
          tmplat=ncFid.variables['grid_corner_lat'][:]
          noff=0
          for n in range(6):
              for j in range(self.npts-1):
                  for i in range(self.npts-1):
                       self.lon_corners[n,j,i]=tmplon[noff,0]
                       self.lon_corners[n,j,i+1]=tmplon[noff,1]
                       self.lon_corners[n,j+1,i+1]=tmplon[noff,2]
                       self.lon_corners[n,j+1,i]=tmplon[noff,3]

                       self.lat_corners[n,j,i]=tmplat[noff,0]
                       self.lat_corners[n,j,i+1]=tmplat[noff,1]
                       self.lat_corners[n,j+1,i+1]=tmplat[noff,2]
                       self.lat_corners[n,j+1,i]=tmplat[noff,3]
                       noff=noff+1

          tmplon=ncFid.variables['grid_center_lon'][:]
          tmplat=ncFid.variables['grid_center_lat'][:]
          noff=0
          for n in range(6):
              for j in range(self.npts-1):
                  for i in range(self.npts-1):
                       self.lon[n,j,i]=tmplon[noff]
                       self.lat[n,j,i]=tmplat[noff]
                       noff=noff+1

       else:
          raise Exception("Unsupported grid file type")

       self.lon_corners=self.lon_corners*m.pi/180.0
       self.lat_corners=self.lat_corners*m.pi/180.0
       self.lon=self.lon*m.pi/180.0
       self.lat=self.lat*m.pi/180.0
       self.xyzc=np.array(convert_to_cart(self.lon_corners,self.lat_corners))
       self.xyz=np.array(convert_to_cart(self.lon,self.lat))

   def getIndices(self,lon,lat):
       npoints = lon.size
       xyz=np.array(convert_to_cart(lon,lat))
       ii=[]
       jj=[]
       iface=[]



       ilb=0
       iub=self.npts-1
       jlb=0
       jub=self.npts-1

       for j in range(npoints):
          for i in range(6):
              in_region=point_in_polygon(xyz[:,j],self.xyz[:,i,0,0], \
                                                 self.xyzc[:,i,jlb,ilb],self.xyzc[:,i,jlb,iub], \
                                                 self.xyzc[:,i,jub,iub],self.xyzc[:,i,jub,ilb])
              if in_region == 1:
                 face=i
                 break
          #now find point
          ilb=0
          iub=self.npts-2
          jlb=0
          jub=self.npts-2
          lnew=ilb
          unew=iub
          for n in range(self.npts-1):
              lold=lnew
              uold=unew
              unew=lold+(uold-lold)//2
              in_sub_region=point_in_polygon(xyz[:,j],self.xyz[:,face,jlb,lnew], \
                                                 self.xyzc[:,face,jlb,lnew],self.xyzc[:,face,jlb,unew+1], \
                                                 self.xyzc[:,face,jub+1,unew+1],self.xyzc[:,face,jub+1,lnew])
              if in_sub_region==1:
                 lnew=lold
                 unew=unew
              else:
                 lnew=unew+1
                 unew=uold
              if unew==lnew:
                 ifound=unew
                 break

          lnew=jlb
          unew=jub
          for n in range(self.npts-1):
              lold=lnew
              uold=unew
              unew=lold+(uold-lold)//2
              in_sub_region=point_in_polygon(xyz[:,j],self.xyz[:,face,lnew,ifound], \
                                                 self.xyzc[:,face,lnew,ifound],self.xyzc[:,face,lnew,ifound+1], \
                                                 self.xyzc[:,face,unew+1,ifound+1],self.xyzc[:,face,unew+1,ifound])
              if in_sub_region==1:
                 lnew=lold
                 unew=unew
              else:
                 lnew=unew+1
                 unew=uold
              if unew==lnew:
                 jfound=unew
                 break

          ii.append(ifound)
          jj.append(jfound)
          iface.append(face)
          print(j)
          print(face,ifound,jfound)
          print(lon[j],lat[j])
          print(lon[j]*180.0/m.pi,lat[j]*180.0/m.pi)
          print(self.lon[face,jfound,ifound]*180.0/m.pi,self.lat[face,jfound,ifound]*180.0/m.pi)
       return (iface,ii,jj)
