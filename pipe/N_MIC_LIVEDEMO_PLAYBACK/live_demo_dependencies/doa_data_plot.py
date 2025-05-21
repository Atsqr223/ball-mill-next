from .glob_vars import *
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.figure import Figure
from mpl_toolkits import mplot3d

def plot_music_2d(p_music,plotlabel):
    #2d theta vs phi plot===========
    fig = Figure(figsize=(5,4), dpi=100)
    #ax = fig.add_subplot(111)
    #ax.plot(p_music)
    #xx = np.linspace(0,360, num=361)
    #annot_max(xx,p_music)
    #plt.ion()
    plt.xticks(np.linspace(0,PHI_INTERVALS-1,10),np.linspace(0,90,10),rotation=90)
    plt.yticks(np.linspace(0,THETA_INTERVALS-1,10),np.linspace(0,360,10))
    plt.xlabel("PHI")
    plt.ylabel("THETA")
    plt.title(plotlabel)
    plt.imshow(p_music, aspect='auto',origin = 'upper', cmap='jet', interpolation='nearest')

def plot_music_3dscatter(p_music,plotlabel):
    #3d scatter====================
    x=[]
    y=[]
    z=[]
    c=[]
    rad = 4.6#6e-3
    theta_index= 0
    for theta in np.linspace(0,360,THETA_INTERVALS):
        phi_index = 0
        for phi in np.linspace(0,90,PHI_INTERVALS):
            x.append(rad*np.sin(phi*np.pi/180)*np.cos(theta*np.pi/180))
            y.append(rad*np.sin(phi*np.pi/180)*np.sin(theta*np.pi/180))
            z.append(rad*np.cos(phi*np.pi/180))
            c.append(p_music[theta_index][phi_index])
            phi_index+=1
        theta_index+=1
    
    fig = Figure(figsize=(10,10))
    ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('jet')
    sctt = ax.scatter3D(x,y,z,alpha=0.8,c=c,cmap=my_cmap)
    plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")

def plot_music_spherical(p_music,plotlabel,fig = Figure(figsize=(10,10)), ax=plt.axes(projection='3d'),plot_elev=30,plot_azim=-45,plot_alpha=0.5,vmin=None,vmax=None,save=False):
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_theta = len(p_music)
    len_phi=len(p_music[0])
    
    theta=np.linspace(0,360,len_theta)
    phi=np.linspace(0,90,len_phi)
    print("Theta and phi before meshgrid:",theta.shape,phi.shape)
    theta,phi = np.meshgrid(theta,phi)
    print("Theta and phi after meshgrid:",theta.shape,phi.shape)
    x=rad*np.sin(phi*np.pi/180)*np.cos(theta*np.pi/180)
    y=rad*np.sin(phi*np.pi/180)*np.sin(theta*np.pi/180)
    z=rad*np.cos(phi*np.pi/180)
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    c=np.empty(x.shape,dtype='float')
    print("color shape:",c.shape)
    print("Theta interva, phi interval: ",len_theta,len_phi)
    
    for Y in range(len_phi):
        for X in range(len_theta):
            c[Y,X] = 0.5
    #fig = Figure(figsize=(10,10))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('jet')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
    else:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
        
    plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")

    #colorbar
    m = cm.ScalarMappable(cmap=cm.jet)
    m.set_array(p_music)
    if vmin != None and vmax !=None:
        m.set_clim(vmin=vmin, vmax=vmax)
    cbar=plt.colorbar(m,ax=plt.gca(),shrink=0.3)
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def plot_music_cylindrical(p_music,plotlabel='test',fig = Figure(figsize=(10,10)), ax=plt.axes(projection='3d'),plot_elev=30,plot_azim=-45,plot_alpha=1,vmin=None,vmax=None,save=False):
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_y = len(p_music)
    len_delta=len(p_music[0])
    
    y_vals=np.linspace(-CYLINDER_LENGTH/2,CYLINDER_LENGTH/2,CYLINDER_Y_INTERVALS)
    delta_vals=np.linspace(-np.pi/2-CYLINDER_CHI+CYLINDER_CHI_OFFSET,-np.pi/2+CYLINDER_CHI+CYLINDER_CHI_OFFSET,CYLINDER_DELTA_INTERVALS)
    print("y and delta before meshgrid:",y_vals.shape,delta_vals.shape)
    y_vals,delta_vals = np.meshgrid(y_vals,delta_vals)
    print("y and delta after meshgrid:",y_vals.shape,delta_vals.shape)

    x=CYLINDER_RADIUS*np.cos(delta_vals)#-np.ones_like(delta_vals)*CYLINDER_X_OFFSET
    y=y_vals
    z=CYLINDER_HEIGHT+CYLINDER_RADIUS*(1+np.sin(delta_vals))
    
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    #c=np.empty(x.shape,dtype='float')
    #print("color shape:",c.shape)
    print("y interva, delta interval: ",len_y,len_delta)
    
    #fig = Figure(figsize=(10,10))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('jet')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    #ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
    else:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
        
    plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")
    
    #colorbar
    m = cm.ScalarMappable(cmap=cm.jet)
    m.set_array(p_music)
    if vmin != None and vmax !=None:
        m.set_clim(vmin=vmin, vmax=vmax)
    cbar=plt.colorbar(m,ax=plt.gca(),shrink=0.3)
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def plot_music_cylindrical_flat(p_music,plotlabel='test',fig = Figure(figsize=(10,10)), ax=plt.axes(projection='3d'),plot_elev=30,plot_azim=-45,plot_alpha=1,vmin=None,vmax=None,save=False,colorbar_enabled=True):
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_y = len(p_music)
    len_delta=len(p_music[0])
    
    y_vals=np.linspace(-CYLINDER_LENGTH/2,CYLINDER_LENGTH/2,CYLINDER_Y_INTERVALS)
    delta_vals=np.linspace(-np.pi/2-CYLINDER_CHI+CYLINDER_CHI_OFFSET,-np.pi/2+CYLINDER_CHI+CYLINDER_CHI_OFFSET,CYLINDER_DELTA_INTERVALS)
    print("y and delta before meshgrid:",y_vals.shape,delta_vals.shape)
    y_vals,delta_vals = np.meshgrid(y_vals,delta_vals)
    print("y and delta after meshgrid:",y_vals.shape,delta_vals.shape)

    x=CYLINDER_RADIUS*np.cos(delta_vals)#-np.ones_like(delta_vals)*CYLINDER_X_OFFSET
    y=y_vals
    z=np.zeros_like(delta_vals)#CYLINDER_HEIGHT+CYLINDER_RADIUS*(1+np.sin(delta_vals))
    
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    #c=np.empty(x.shape,dtype='float')
    #print("color shape:",c.shape)
    print("y interva, delta interval: ",len_y,len_delta)
    
    #fig = Figure(figsize=(10,10))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('gist_heat')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    #ax.plot_surface(x,y,z,facecolors=cm.hot(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.gist_heat(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
    else:
        ax.plot_surface(x,y,z,facecolors=cm.gist_heat(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
        
    plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel(None)
    ax.set_zlim([0, 1])
    #ax.set_yticks(np.arange(-int(np.ceil(CYLINDER_LENGTH/2)),int(np.ceil(CYLINDER_LENGTH/2)),2))
    ax.set_ylim([-CYLINDER_LENGTH/2,CYLINDER_LENGTH/2])
    ax.set_xlim([-CYLINDER_RADIUS,CYLINDER_RADIUS])
    ax.set_zticks([])
    #colorbar
    if colorbar_enabled:
        m = cm.ScalarMappable(cmap=cm.gist_heat)
        m.set_array(p_music)
        if vmin != None and vmax !=None:
            m.set_clim(vmin=vmin, vmax=vmax)
        cbar=plt.colorbar(m,ax=plt.gca(),shrink=0.5)
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def plot_music_plane(p_music,PLANE_HEIGHT,plotlabel='test',fig = Figure(figsize=(10,10)),
                     ax=plt.axes(projection='3d'),plot_elev=90,plot_azim=0,plot_alpha=1,vmin=None,vmax=None,save=False): #inferno, jet
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_y = len(p_music)
    len_x=len(p_music[0])
    
    y_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    x_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    print("y and x before meshgrid:",y_vals.shape,x_vals.shape)
    y_vals,x_vals = np.meshgrid(y_vals,x_vals)
    print("y and x after meshgrid:",y_vals.shape,x_vals.shape)

    x=x_vals
    y=y_vals
    z=np.ones_like(y_vals)*PLANE_HEIGHT
    
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    #c=np.empty(x.shape,dtype='float')
    #print("color shape:",c.shape)
    print("y interva, x interval: ",len_y,len_x)
    
    #fig = Figure(figsize=(10,10))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('jet')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    else:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")
    
    #colorbar

    #colorbar

    m = cm.ScalarMappable(cmap=cm.jet)
    m.set_array(p_music)
    if vmin != None and vmax !=None:
        m.set_clim(vmin=vmin, vmax=vmax)
    cbar=plt.colorbar(m,ax=plt.gca())#,shrink=0.3)
    
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def plot_music_plane_flat(p_music,PLANE_HEIGHT,plotlabel='test',fig=0,
                     ax=0,plot_elev=90,plot_azim=0,plot_alpha=1,vmin=None,vmax=None,save=False,title_enabled=True,colorbar_enabled=True): #inferno, jet
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_y = len(p_music)
    len_x=len(p_music[0])
    
    y_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    x_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    print("y and x before meshgrid:",y_vals.shape,x_vals.shape)
    y_vals,x_vals = np.meshgrid(y_vals,x_vals)
    print("y and x after meshgrid:",y_vals.shape,x_vals.shape)

    x=x_vals
    y=y_vals
    z=np.zeros_like(y_vals)
    
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    #c=np.empty(x.shape,dtype='float')
    #print("color shape:",c.shape)
    print("y interva, x interval: ",len_y,len_x)
    
    #fig = Figure(figsize=(1,1))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('jet')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    else:
        ax.plot_surface(x,y,z,facecolors=cm.jet(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
    if title_enabled:
        plt.title(plotlabel)
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel(None)
    ax.set_zlim([0, 1])
    #ax.set_yticks(np.arange(-60,60,20))
    ax.set_ylim([-60,60])
    ax.set_xlim([-60,60])
    #ax.set_xticks(np.arange(-60,60,20))
    ax.set_zticks([])
    #colorbar
    if colorbar_enabled:
        m = cm.ScalarMappable(cmap=cm.jet)
        m.set_array(p_music)
        if vmin != None and vmax !=None:
            m.set_clim(vmin=vmin, vmax=vmax)
        cbar=plt.colorbar(m,ax=plt.gca(),shrink=0.5)
    
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def plot_music_plane_flat_improc(p_music,PLANE_HEIGHT,plotlabel='test',fig = Figure(figsize=(10,10)),
                     ax=plt.axes(projection='3d'),plot_elev=90,plot_azim=0,plot_alpha=1,vmin=None,vmax=None,save=False,title_enabled=True,colorbar_enabled=True): #inferno, jet
    #3d surface plot=================
    rad = 4.6#6e-3
    x=[]
    y=[]
    z=[]
    c=[]
    print("pmusic len: ",len(p_music),len(p_music[0]))
    
    len_y = len(p_music)
    len_x=len(p_music[0])
    
    y_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    x_vals=np.linspace(-PLANE_LENGTH/2,PLANE_LENGTH/2,PLANE_LENGTH_INTERVALS)
    print("y and x before meshgrid:",y_vals.shape,x_vals.shape)
    y_vals,x_vals = np.meshgrid(y_vals,x_vals)
    print("y and x after meshgrid:",y_vals.shape,x_vals.shape)

    x=x_vals
    y=y_vals
    z=np.zeros_like(y_vals)
    
    print("x and y and z shapes: ",x.shape,y.shape,z.shape)

    #c=np.empty(x.shape,dtype='float')
    #print("color shape:",c.shape)
    print("y interva, x interval: ",len_y,len_x)
    
    #fig = Figure(figsize=(10,10))
    #ax = plt.axes(projection='3d')
    my_cmap = plt.get_cmap('hot')
    ax.view_init(elev=plot_elev, azim=plot_azim) #uncomment for iso plot
    if vmin == None or vmax == None:
        ax.plot_surface(x,y,z,facecolors=cm.hot(((p_music-p_music.min())/(p_music.max()-p_music.min())).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)

    else:
        ax.plot_surface(x,y,z,facecolors=cm.hot(((p_music-vmin)/(vmax-vmin)).T), edgecolor = 'none',alpha=plot_alpha,linewidth=0,rstride=1,cstride=1,shade=False)
    if title_enabled:
        plt.title(plotlabel)
    ax.set_xlabel("X (cm)",fontsize=20)
    ax.set_ylabel("Y (cm)",fontsize=20)
    ax.set_zlabel(None)
    ax.set_zlim([0, 1])
    ax.set_yticks(np.arange(-60,60,20))
    ax.set_ylim([-60,60])
    ax.set_xlim([-60,60])
    ax.set_xticks(np.arange(-60,60,20))
    ax.set_zticks([])
    plt.tick_params(axis='x',which='major',labelsize=20)
    plt.tick_params(axis='y',which='major',labelsize=20)
    #colorbar
    if colorbar_enabled:
        m = cm.ScalarMappable(cmap=cm.hot)
        m.set_array(p_music)
        if vmin != None and vmax !=None:
            m.set_clim(vmin=vmin, vmax=vmax)
        cbar=plt.colorbar(m,ax=plt.gca(),shrink=0.5)
    
    if save:
        plt.savefig(f"./tempplot/{plotlabel}.png")
        #plt.plot(p_music,label = plotlabel)
        #
    return fig,ax

def draw_plate(ax,h,s_len=64):
    # Define the side length and height
    side_length = s_len
    height = h

    # Calculate the half side length
    half_side = side_length / 2

    # Define the corner points of the square (centered at (0, 0))
    corner_points = np.array([
        [-half_side, -half_side, h],
        [half_side, -half_side, h],
        [half_side, half_side,h],
        [-half_side, half_side, h]
    ])


    # Plot the square
    for i in range(4):
        ax.plot([corner_points[i, 0], corner_points[(i + 1) % 4, 0]],
                [corner_points[i, 1], corner_points[(i + 1) % 4, 1]],
                [corner_points[i, 2], corner_points[(i + 1) % 4, 2]], color='white')

    # Set the z-coordinate for the top face (parallel to xy-plane)
    z_top = height
    top_square = np.array([
        [point[0], point[1], z_top] for point in corner_points
    ])

    # Plot the top face
    for i in range(4):
        ax.plot([top_square[i, 0], top_square[(i + 1) % 4, 0]],
                [top_square[i, 1], top_square[(i + 1) % 4, 1]],
                [top_square[i, 2], top_square[(i + 1) % 4, 2]], color='white')

