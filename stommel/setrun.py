# encoding: utf-8
"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

import clawpack.clawutil.clawdata as data
import numpy as np

import clawpack.geoclaw.surge as surge

days2seconds = lambda days: days * 60.0**2 * 24.0
seconds2days = lambda seconds: seconds / (60.0**2 * 24.0)

#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)

    #------------------------------------------------------------------
    # Problem-specific parameters to be written to setprob.data:
    #------------------------------------------------------------------

    #probdata = rundata.new_UserData(name='probdata',fname='setprob.data')

    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------

    rundata = setgeo(rundata)   # Defined below

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------

    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = num_dim

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = 0.0
    clawdata.upper[0] = 1000e3
    
    clawdata.lower[1] = 0.0
    clawdata.upper[1] = 1000e3

    # Number of grid cells:
    clawdata.num_cells[0] = 100
    clawdata.num_cells[1] = 100

    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 4 + 3 + 2

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 0



    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0

    # Restart from checkpoint file of a previous run?
    # Note: If restarting, you must also change the Makefile to set:
    #    RESTART = True
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False               # True to restart from prior results
    clawdata.restart_file = 'fort.chk00006'  # File to use for restart data


    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.tfinal = days2seconds(100.0)
        clawdata.num_output_times = 100

        clawdata.output_t0 = True  # output at initial (or restart) time?
        

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = [0.5, 1.0]

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 1
        clawdata.output_t0 = True



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 2



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.016

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.75
    clawdata.cfl_max = 1.0
    # clawdata.cfl_desired = 0.25
    # clawdata.cfl_max = 0.5

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 5000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    clawdata.limiter = ['mc', 'mc', 'mc']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'godunov'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'wall'
    clawdata.bc_upper[0] = 'wall'

    clawdata.bc_lower[1] = 'wall'
    clawdata.bc_upper[1] = 'wall'


    # ---------------
    # AMR parameters:
    # ---------------


    # max number of refinement levels:
    clawdata.amr_levels_max = 5

    # List of refinement ratios at each level (length at least mxnest-1)
    clawdata.refinement_ratios_x = [2,2,3,4,4,4]
    clawdata.refinement_ratios_y = [2,2,3,4,4,4]
    clawdata.refinement_ratios_t = [2,2,3,4,4,4]


    # Specify type of each aux variable in clawdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    clawdata.aux_type = ['center','capacity','yleft','center','center','center',
                         'center', 'center', 'center']


    # Flag using refinement routine flag2refine rather than richardson error
    clawdata.flag_richardson = False    # use Richardson?
    clawdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    clawdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    clawdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    clawdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    clawdata.verbosity_regrid = 0  

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif clawdata.checkpt_style == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = [0.1,0.15]

    elif clawdata.checkpt_style == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5


    #  ----- For developers ----- 
    # Toggle debugging print statements:
    clawdata.dprint = False      # print domain flags
    clawdata.eprint = False      # print err est flags
    clawdata.edebug = False      # even more err est flags
    clawdata.gprint = False      # grid bisection/clustering
    clawdata.nprint = False      # proper nesting output
    clawdata.pprint = False      # proj. of tagged points
    clawdata.rprint = False      # print regridding summary
    clawdata.sprint = False      # space/memory output
    clawdata.tprint = False      # time step reporting each level
    clawdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    return rundata
    # end of function setrun
    # ----------------------


#-------------------
def setgeo(rundata):
#-------------------
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        geodata = rundata.geodata
    except:
        print "*** Error, this rundata has no geodata attribute"
        raise AttributeError("Missing geodata attribute")

    # == setgeo.data values ==
    geodata.variable_dt_refinement_ratios = True

    geodata.gravity = 9.81
    geodata.coordinate_system = 1
    geodata.earth_radius = 6367.5e3
    geodata.coriolis_forcing = True
    geodata.theta_0 = 45.0

    # == settsunami.data values ==
    geodata.dry_tolerance = 1.e-2
    geodata.wave_tolerance = 5.e-1
    geodata.speed_tolerance = [1e10,1e10,1e10,1e10,1e10]
    geodata.deep_depth = 2.e2
    geodata.max_level_deep = 4
    geodata.friction_forcing = 1
    geodata.manning_coefficient = 1e-6
    geodata.friction_depth = 1.e10

    # == settopo.data values ==
    # Analytic bathymetry
    geodata.test_topography = 1
    geodata.topo_location = 0.0
    geodata.topo_left = -1000.0
    geodata.topo_right = -1000.0
    
    return rundata
    # end of function setgeo
    # ----------------------

def set_storm(rundata):

    data = rundata.stormdata

   # Physics parameters
    data.rho_air = 1.0              # Density of air (rho is not implemented above)
    data.ambient_pressure = 101.5e3 # Nominal atmos pressure

    # Source term controls
    data.wind_forcing = True
    data.pressure_forcing = True

    # AMR parameters, in m/s and meters respectively
    data.wind_refine = [20.0,40.0,60.0]
    data.R_refine = [60.0e3,40e3,20e3]
    
    # Storm parameters
    data.storm_type = 3 # Stommel wind field

    # Stommel wind field
    data.A = 0.2 / 1.2

    return data


def set_friction(rundata):

    data = rundata.frictiondata

    # Variable friction
    data.variable_friction = False

    return data

if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    if len(sys.argv) == 2:
        rundata = setrun(sys.argv[1])
    else:
        rundata = setrun()

    rundata.add_data(surge.data.SurgeData(),'stormdata')
    set_storm(rundata)
    rundata.add_data(surge.data.FrictionData(),'frictiondata')
    set_friction(rundata)

    rundata.write()

