// Austrdoc.h : interface of the CAustriaDoc class
//
/////////////////////////////////////////////////////////////////////////////
#pragma pack(1)

class CLeCroy_Trig_Time
{
public:
	double Trig_Time;
	double Trig_Offset;
};

#pragma pack()

class C_Yokagawa_Ch_Array
{
public:
	int		Yok_Ch_Num;
	long	Yok_Block_Size;
	double	Yok_Vresolution;
	double  Yok_VertOffset;
	char	Yok_VertDesc[40];
	double	Yok_SaveVresolution;
	double  Yok_SaveVertOffset;
	char	Yok_SaveVertDesc[40];
	BOOL	Yok_UnitsHaveChanged;
	double	Yok_Hresolution;
	double	Yok_Hoffset;
	char	Yok_Date[16];
	char	Yok_Time[16];
};

class C_Nicolet_Ch_Array
{
public:
	int		Nic_Ch_Num;
	long	Nic_Block_Size;
	double	Nic_Vresolution;
	double  Nic_VertOffset;
	char	Nic_VertDesc[40];
	double	Nic_SaveVresolution;
	double  Nic_SaveVertOffset;
	char	Nic_SaveVertDesc[40];
	BOOL	Nic_UnitsHaveChanged;
	double	Nic_Hresolution;
	double	Nic_Hoffset;
	char	Nic_Date[16];
	char	Nic_Time[16];
};

#pragma pack(1)
class CGage_Template_Type
{
public:
	char			Gage_HeaderTextID[23];		//"ElectricFieldSystem1.00"
	char			Gage_DateTime[14];			//ddmmyyyyHHMMSS
	double			Gage_SampleRate;			//samples per second
	double			Gage_SegmentSize;			//samples
	unsigned short	Gage_ClockMode;				//enum 1=External, 2=10MHz reference
	double			Gage_TriggerTimeout;		//microseconds
	double			Gage_TriggerHoldoff;		//samples
	double			Gage_Depth;					//samples, SegmentSize - depth = pretrigger
	double			Gage_TriggerDelay;			//samples
	unsigned int	Gage_PostTriggerTimeout;	//milliseconds
	unsigned int	Gage_SegmentCount;			//number of segments set by program
	BYTE			Gage_NumChannels;			//enum 1= single channel, 2 = dual, 4 = quad, 8 = octal
	BYTE			Gage_Slope;					//enum 0 = rising, 1 = falling
	unsigned int	Gage_ExternalRange;			//millivolts - should be 2000 or 10000
	int				Gage_TriggerLevel;			//percent - percentage of the input range (-100 <---> +100)
	BYTE			Gage_ExternalCoupling;		//enum 0 = DC, 1 = AC
	int				Gage_TriggerSource;			//channel number - first channel is 0, also zero if Ext. Src. or Dis. Src. is TRUE
	BYTE			Gage_ExternalImpedance;		//enum 0 = Hi Z, 1 = 50 Ohms
	BYTE			Gage_ExternalTrigger;		//enum 0 = internal trigger, 1 = external trigger
	BYTE			Gage_DisableTrigger;		//enum 0 = trigger disabled, 1 = trigger enabled
	unsigned int	Gage_TickFrequency;			//Hz - trigger time counter clock rate
	unsigned int	Gage_ExternalTriggerCount;	//Reports number of triggers that the system "believes" to be valid.

};

class CGage_Channel_Template_Type				// one the blocks below for each channel
{
public:

	BYTE			GageCh_Coupling;			//enum 0 = DC, 1 = AC
	unsigned int	GageCh_Range;				//input range in mv, e.g. +/- 1V = 2000
	BYTE			GageCh_DifferentialInput;	//enum 0 = single ended, 1 = differential
	unsigned int	GageCh_Impedance;			//Ohms, should be 50 or 1,000,000
	BYTE			GageCh_DirectToADC;			//enum 0 = DirectToADC active, 1 = not active
	unsigned int	GageCh_DCOffset;			//DC offset in mV. If DC offset not supported, returns 0
	unsigned int	GageCh_Filter;				//Not specified. Probably for future feature. returns 0


};

/*
There will be one trigger timestamp per REQUESTED segment, whether an external trigger event occurred or not.
The post-trigger timeout sets the interval between the first trigger and the time at which the system internally
triggers the remaining segments so that the capture completes cleanly.  The data collected here is saved, just in case a real
trigger occurs during that process.						
*/

class CGage_Trigger_Timestamps_Type

{
public:
	double			Gage_Timestamp;				//microseconds - value of the timesstamp counter when the trigger occurs
												//the values are irrevelant unless the difference is taken
};


/*
Reports the actual start time, in samples relative to the trigger.  This may be different (usually earlier) than requested
due to data packing in the buffer. There will be one time reported per segment, per channel.  Each is an IEEE Double, 8 bytes,
and there are #CH x # SEGs of them.  Note that all requested segments will be reported, whether externally triggered or not.
If an event occurs with 3 triggers but 10 were set, 10 trigger times, actual start times, and actual lengths will be reported.		
Data order: Start time for the first segment, next segment, next segment, so until all segments in first channel.  
Next, first segment in second channel and so on.		
*/

class CGage_Actual_Starts_Type

{
public:
	double			Gage_ActualStart; 
};

//Reports the actual segment length in samples.  This may differ from the requested segment size due to storage in the buffer. Same data order as Starts.

class CGage_Actual_Length_Type

{
public:
	double			Gage_ActualLength;			//total segment length in samples

};




class CLeCroy_Template_Type
{
public:
	char dummy[11];
	char Descriptor_Name[16];
	char Template_Name[16];
	short Comm_Type;
									/*	enum Comm_Type_def
										{
											byte,
											word
										}Comm_Type;*/
	short Comm_Order;
									/*	enum Comm_Order_def
										{
											HiFirst,
											LoFirst
										}Comm_Order;*/
	long Wave_Descriptor;
	long User_Text;
	long Res_Desc1;
	long Trig_Time_Array;
	long Ris_Time_Array;
	long Res_Array1;
	long Wave_Array_1;
	long Wave_Array_2;
	long Res_Array2;
	long Res_Array3;
	char Instrument_Array[16];
	long Instrument_Number;
	char Trace_Label[16];
	short Reserved1;
	short Reserved2;
	long Wave_Array_Count;
	long Pnts_Per_Screen;
	long First_Valid_Point;
	long Last_Valid_Point;
	long First_Point;
	long Sparsing_Factor;
	long Segment_Index;
	long Subarray_Count;
	long Sweeps_Per_Acq;
	short Points_Per_Pair;
	short Pair_Offset;
	float Vertical_Gain;
	float Vertical_Offset;
	float Max_Value;
	float Min_Value;
	short Nominal_Bits;
	short Nom_Subarray_Count;
	float Horiz_Interval;
	double Horiz_Offset;
	double Pixel_Offset;
	char VertUnit[48];
	char HorUnit[48];
	float Horiz_Uncertainty;
	double Time_Stamp_Seconds;
	BYTE Time_Stamp_Minutes;
	BYTE Time_Stamp_Hours;
	BYTE Time_Stamp_Days;
	BYTE Time_Stamp_Months;
	short Time_Stamp_Year;
	short Time_Stamp_unused;
	float Acq_Duration;
	short LeCroy_Record_Type;
								/*	enum Record_Type
									{
										SingleSweep,
										Interleaved,
										Histogram,
										Graph,
										Filter_Coefficient,
										Complex,
										Extrema,
										Sequence_Obsolete,
										Centered_RIS,
										Peak_Detect
									}Lecroy_Record_Type;*/
	short Processing_Done;
								/*	enum Processing_Done_Type
									{
										No_Processing,
										Fir_Filter,
										Interpolated,
										Sparsed,
										Autoscaled,
										No_Result,
										Rolling,
										Cumulative
									}Processing_Done;*/
	short Reserved5;
	short RIS_Sweeps;
	short TimeBase;
								/*	enum TimeBase_Type
									{
										tb1_ps,
										tb2_ps,
										tb5_ps,
										tb10_ps,
										tb20_ps,
										tb50_ps,
										tb100_ps,
										tb200_ps,
										tb500_ps,
										tb1_ns,
										tb2_ns,
										tb5_ns,
										tb10_ns,
										tb20_ns,
										tb50_ns,
										tb100_ns,
										tb200_ns,
										tb500_ns,
										tb1_us,
										tb2_us,
										tb5_us,
										tb10_us,
										tb20_us,
										tb50_us,
										tb100_us,
										tb200_us,
										tb500_us,
										tb1_ms,
										tb2_ms,
										tb5_ms,
										tb10_ms,
										tb20_ms,
										tb50_ms,
										tb100_ms,
										tb200_ms,
										tb500_ms,
										tb1_s,
										tb2_s,
										tb5_s,
										tb10_s,
										tb20_s,
										tb50_s,
										tb100_s,
										tb200_s,
										tb500_s,
										tb1_ks,
										tb2_ks,
										tb5_ks,
										External=100
									}TimeBase;*/
	short Vert_Coupling;
								/*	enum Vert_Coupling_Type
									{
										DC_50_Ohms,
										DC_ground,
										DC_1MOhm,
										AC_ground,
										AC_1MOhm
									}Vert_Coupling;*/
	float Probe_Att;
	short Fixed_Vert_Gain;
								/*	enum Fixed_Vert_Gain_Type
									{
										g1_uV_Per_Div,
										g2_uV_Per_Div,
										g5_uV_Per_Div,
										g10_uV_Per_Div,
										g20_uV_Per_Div,
										g50_uV_Per_Div,
										g100_uV_Per_Div,
										g200_uV_Per_Div,
										g500_uV_Per_Div,
										g1_mV_Per_Div,
										g2_mV_Per_Div,
										g5_mV_Per_Div,
										g10_mV_Per_Div,
										g20_mV_Per_Div,
										g50_mV_Per_Div,
										g100_mV_Per_Div,
										g200_mV_Per_Div,
										g500_mV_Per_Div,
										g1_V_Per_Div,
										g2_V_Per_Div,
										g5_V_Per_Div,
										g10_V_Per_Div,
										g20_V_Per_Div,
										g50_V_Per_Div,
										g100_V_Per_Div,
										g200_V_Per_Div,
										g500_V_Per_Div,
										g1_kV_Per_Div
									}Fixed_Vert_Gain;*/
	short BandWidth_Limit;
								/*	enum BandWidth_Limit_Type
									{
										off,
										on
									}BandWidth_Limit;*/
	float Vertical_Vernier;
	float Acq_Vertical_Offset;
	short Wave_Source;
								/*	enum Wave_Source_Type
									{
										Channel_1,
										Channel_2,
										Channel_3,
										Channel_4,
										unknown=9
									}Wave_Source;*/
};

class CNicolet_Header_Type
{
	public:

		short	HeaderVersion;
		short	NChan;
		short	NRec;
		long	Length;
		long	NSkip;
		long	NSamp;
		short	SampType;
		char	XUnits[8];
		double	X0;
		double	XStep;
		BYTE	Hours;
		BYTE	Minutes;
		BYTE	Seconds;
		BYTE	Years;	// since 1980
		BYTE	Month;
		BYTE	Day;
		short	NEvents;
		short	NSegments;
		long	SegmentOffset;
		char	SegmentsXUnits[8];
		long	RecInfoOffset;
		char	Reserved[186];
		char	Y_Ch1_Name[7];
		char	Y_Ch1_Units[7];
		float	Y_Ch1_Y0;
		float	Y_Ch1_YStep;
		float	Y_Ch1_Max;
		float	Y_Ch1_Min;
		short	Y_Ch1_Reserved;
		char	Y_Ch2_Name[7];
		char	Y_Ch2_Units[7];
		float	Y_Ch2_Y0;
		float	Y_Ch2_YStep;
		float	Y_Ch2_Max;
		float	Y_Ch2_Min;
		short	Y_Ch2_Reserved;
};

#pragma pack()

class CVInfo 
{
	public:
		float TimePerSample;
		double StartTime;
		double EndTime;
		double SaveStartTime;
		double SaveEndTime;
		double VertScale;
		double SaveVertScale;
		double VertOffset;
		double SaveVertOffset;
		double VertMin;
		double VertMax;
		double VertLockMin;
		double VertLockMax;
		double LeftCursorTime;
		double LeftCursorAmp;
		double RightCursorTime;
		double RightCursorAmp;
		double Xmult;
		double Ymult;
		double Ydiff;
		double Ymin;
		int Cnum;
		int ActualCnum;
		int Channels;
		long BytesInHeader;
		unsigned long PointsPerChannel;
		int BytesPerPoint;
		int ByteOrder;
		unsigned int ValidDisplayPoints;
		COLORREF ViewBackColor;
		COLORREF ViewTextColor;
		COLORREF ViewLineColor;
		BOOL DoMaxMin;
		BOOL measure;
		BOOL VertLock;
		BOOL Segmented;
		BOOL Saturated;
		BOOL ZeroPlot;
		BOOL SnapToGrid;
		BOOL fmd;
		BOOL fme;
		BOOL fdq;
		BOOL sef;
		int NumSegments;
		int CurrentSegment;
		CLeCroy_Template_Type* ptrLeCroyData;
		CLeCroy_Trig_Time* ptrTrigTimes;
		C_Yokagawa_Ch_Array* ptrYokChArray;
		C_Nicolet_Ch_Array* ptrNicChArray;
		CNicolet_Header_Type* ptrNicoletData;
		CGage_Template_Type* ptrGageData;
		CGage_Channel_Template_Type* ptrGageChannelData;
		char LeCroyInstArray[16];
		char VertDesc[40];
		char ViewDate[16];
		char ViewTime[16];
};

//How many display points do we want to use
const long DISPLAY_POINTS=1000;
const long MAX_BUFFER_SIZE = 524288*2;

class CAustriaDoc : public CDocument
{
protected: // create from serialization only
	CAustriaDoc();
	DECLARE_DYNCREATE(CAustriaDoc)

// Attributes
public:

// Operations
public:
	static int DocCount;  	//count of how many documents are open
	long hdrlen;
	int databytes;
	enum specialtype
	{
		none,
		lecroy,
		nicolet,
		austrian,
		adtek,
		yokogawa,
		gage
	} SpecialFile;

	CVInfo ViewInfo;	//this structure holds the parms for locking multiple views together
// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAustriaDoc)
	public:
	virtual BOOL OnOpenDocument(LPCTSTR lpszPathName);
	virtual void ReportSaveLoadException(LPCTSTR lpszPathName, CException* e, BOOL bSaving, UINT nIDPDefault);
	virtual void OnCloseDocument();
	//}}AFX_VIRTUAL

// Implementation
public:
	int m_NumOpenViews;
	//BOOL CAustriaDoc::ExportData(CVInfo* pInfo, double ExStartTime, double ExEndTime, int ExportCh[], int ExportChSize, int ExportType);

	virtual CString GetMyFileName();
	VOID SyncUs(DOUBLE StartTime, DOUBLE EndTime, int Segment);
	virtual VOID SetSyncFlag(BOOL SyncFlag);
	virtual BOOL AmISynced();
	BOOL SyncViews;
	virtual ~CAustriaDoc();
	virtual void Serialize(CArchive& ar);   // overridden for document i/o
	//virtual CPoint* GetBufPtr();
	virtual CVInfo* GetViewInfo();
	virtual CVInfo DocGetInfo();
	virtual BOOL GetAllData(CVInfo* pInfo, CPoint* buf);
	virtual long GetFileSize();
	static CAustriaDoc * GetDoc();
#ifdef _DEBUG
	virtual void AssertValid() const;
	virtual void Dump(CDumpContext& dc) const;
#endif

protected:

  	//CPoint *Lockbuf;		//my pointer for the buffer each instance of the doc class will use

	char *fbyteptr;
	short *fwordptr;
	long *flongptr;
	CFile myFile;

// Generated message map functions
protected:
	//{{AFX_MSG(CAustriaDoc)
	afx_msg void OnViewMoveLeft();
	afx_msg void OnViewMoveRight();
	afx_msg void OnWindowOpenAllChannels();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////
